import os
from datetime import datetime
from redis import Redis
from rq import Queue, Worker
from rq.job import Job

from models import db, Document, Summary
from utils.pdf_processor import PDFProcessor
from utils.openai_client import OpenAIClient


# Redis connection
redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
task_queue = Queue('deepread', connection=redis_conn)


def enqueue_document_processing(document_id: int):
    """Enqueue a document processing job"""
    job = task_queue.enqueue(
        process_document_task,
        document_id,
        job_timeout='30m'  # 30 minutes timeout
    )
    return job


def get_job_status(job_id: str):
    """Get status of a job"""
    try:
        job = Job.fetch(job_id, connection=redis_conn)

        status = {
            'job_id': job_id,
            'status': job.get_status(),
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'ended_at': job.ended_at.isoformat() if job.ended_at else None,
            'result': job.result,
            'exc_info': job.exc_info
        }

        # Get progress from job meta
        if hasattr(job, 'meta'):
            status['progress'] = job.meta.get('progress', 0)

        return status

    except Exception as e:
        return {
            'job_id': job_id,
            'status': 'unknown',
            'error': str(e)
        }


def process_document_task(document_id: int):
    """
    Main task to process a document
    This runs in the background via RQ
    """
    from app import app

    with app.app_context():
        try:
            # Get document
            document = Document.query.get(document_id)
            if not document:
                raise Exception(f"Document {document_id} not found")

            # Update status
            document.status = 'processing'
            document.progress = 0
            db.session.commit()

            # Initialize processors
            pdf_processor = PDFProcessor(document.file_path)
            openai_client = OpenAIClient()

            # Get total pages
            total_pages = pdf_processor.get_total_pages()
            document.total_pages = total_pages
            db.session.commit()

            # Detect chapters
            chapters = pdf_processor.detect_chapters()

            total_steps = len(chapters) + 1  # chapters + overall summary
            current_step = 0

            # Process each chapter
            chapter_summaries = []

            for chapter in chapters:
                current_step += 1

                # Extract text from chapter
                text = pdf_processor.extract_text_from_range(
                    chapter['start_page'],
                    chapter['end_page']
                )

                # Check if we need OCR (scanned pages)
                if len(text.strip()) < 100:
                    # Try OCR on first page of chapter
                    try:
                        ocr_text = pdf_processor.ocr_page(chapter['start_page'])
                        if ocr_text:
                            text = ocr_text
                    except:
                        pass  # OCR failed, continue with extracted text

                # Summarize chapter
                if text.strip():
                    # For very long chapters, use vision API with sample pages
                    if len(text) > 10000:
                        context = f"Chapter {chapter['number']}: {chapter['title']}"
                        result = openai_client.summarize_text(text[:10000], context=context)
                    else:
                        context = f"Chapter {chapter['number']}: {chapter['title']}"
                        result = openai_client.summarize_text(text, context=context)

                    # Save chapter summary
                    summary = Summary(
                        document_id=document_id,
                        summary_type='chapter',
                        chapter_number=chapter['number'],
                        chapter_title=chapter['title'],
                        start_page=chapter['start_page'],
                        end_page=chapter['end_page'],
                        content=result['summary'],
                        keywords=result['keywords']
                    )

                    db.session.add(summary)
                    chapter_summaries.append(result['summary'])

                # Update progress
                progress = int((current_step / total_steps) * 100)
                document.progress = progress
                db.session.commit()

            # Create overall summary
            if chapter_summaries:
                overall_result = openai_client.create_overall_summary(chapter_summaries)

                overall_summary = Summary(
                    document_id=document_id,
                    summary_type='overall',
                    content=overall_result['summary'],
                    keywords=overall_result['keywords']
                )

                db.session.add(overall_summary)

            # Mark as completed
            document.status = 'completed'
            document.progress = 100
            document.completed_at = datetime.utcnow()
            db.session.commit()

            return {
                'status': 'success',
                'document_id': document_id,
                'total_pages': total_pages,
                'chapters_processed': len(chapters)
            }

        except Exception as e:
            # Mark as failed
            document.status = 'failed'
            document.error_message = str(e)
            db.session.commit()

            raise Exception(f"Error processing document {document_id}: {str(e)}")


def start_worker():
    """Start an RQ worker (for development)"""
    from app import app

    with app.app_context():
        worker = Worker([task_queue], connection=redis_conn)
        worker.work()


if __name__ == '__main__':
    # Run worker
    start_worker()
