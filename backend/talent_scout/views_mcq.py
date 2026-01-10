"""
MCQ Screening API Endpoints

Implements the 5+3 strategy for technical screening:
- Generate MCQs for each skill
- Submit and evaluate MCQ answers
- Generate objective questions
- Calculate skill ratings
- Download PDF reports
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings
import logging
import json

from talent_scout.models import CandidateSession
from talent_scout.services.mcq_service import get_mcq_service
from talent_scout.services.pdf_service import get_pdf_generator
from talent_scout.services.groq_service import get_groq_service

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_mcqs(request, session_id):
    
    try:
        session = get_object_or_404(CandidateSession, session_id=session_id)
        
        if not session.tech_stack or len(session.tech_stack) == 0:
            return Response({
                'error': 'No tech stack found. Please complete profile gathering first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mcq_service = get_mcq_service()
        
        # Generate MCQs for each skill
        all_mcqs = {}      # For frontend (sanitized)
        full_mcqs = {}     # For backend (with answers)
        total_questions = 0
        
        for skill in session.tech_stack:
            logger.info(f"Generating MCQs for skill: {skill}")
            mcqs, metadata = mcq_service.generate_mcqs_for_skill(
                skill=skill,
                experience_level=session.experience_level or "mid"
            )
            
            # VALIDATION: Ensure strictly that correct_answer is one of the options
            for mcq in mcqs:
                if mcq['correct_answer'] not in mcq['options']:
                    logger.warning(f"Correct answer '{mcq['correct_answer']}' not found in options for {skill}. Defaulting to first option.")
                    mcq['correct_answer'] = mcq['options'][0]

            # Store full version for backend
            full_mcqs[skill] = mcqs
            
            # Create sanitized version for frontend
            mcqs_without_answers = []
            for mcq in mcqs:
                mcq_copy = mcq.copy()
                mcq_copy.pop('correct_answer', None)
                mcq_copy.pop('explanation', None) # Also hide explanation until answered
                mcqs_without_answers.append(mcq_copy)
            
            all_mcqs[skill] = mcqs_without_answers
            total_questions += len(mcqs)
        
        # Save validated questions to session
        session.mcq_questions = full_mcqs
        session.save()
        
        logger.info(f"Generated {total_questions} MCQs for session {session_id}")
        
        return Response({
            'mcq_questions': all_mcqs,
            'total_questions': total_questions,
            'skills': session.tech_stack
        })
        
    except Exception as e:
        logger.error(f"Failed to generate MCQs: {str(e)}")
        return Response({
            'error': f'Failed to generate MCQs: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_mcq_answer(request, session_id):
    try:
        session = get_object_or_404(CandidateSession, session_id=session_id)
        
        # Get request data
        skill = request.data.get('skill')
        question_index = request.data.get('question_index')
        user_answer = request.data.get('answer')
        
        if not all([skill, question_index is not None, user_answer]):
            return Response({
                'error': 'Missing required fields: skill, question_index, answer'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the MCQ from session
        if skill not in session.mcq_questions:
            return Response({
                'error': f'No MCQs found for skill: {skill}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if question_index >= len(session.mcq_questions[skill]):
            return Response({
                'error': 'Invalid question index'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mcq = session.mcq_questions[skill][question_index]
        
        # Evaluate answer
        # Evaluate answer (Simple direct check)
        correct_answer = mcq.get('correct_answer', '').strip()
        user_answer_cleaned = user_answer.strip()
        
        is_correct = user_answer_cleaned.lower() == correct_answer.lower()
        
        evaluation = {
            "is_correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "explanation": mcq.get("explanation", ""),
            "difficulty": mcq.get("difficulty", "medium"),
            "score": 1.0 if is_correct else 0.0
        }
        
        # Store answer in session
        if not session.mcq_answers:
            session.mcq_answers = {}
        if skill not in session.mcq_answers:
            session.mcq_answers[skill] = []
        
        # Add evaluation result
        session.mcq_answers[skill].append(evaluation)
        session.save()
        
        # Calculate statistics
        total_answered = sum(len(answers) for answers in session.mcq_answers.values())
        total_correct = sum(
            sum(1 for ans in answers if ans.get('is_correct', False))
            for answers in session.mcq_answers.values()
        )
        
        logger.info(
            f"MCQ answer submitted for session {session_id}. "
            f"Correct: {evaluation['is_correct']}, Total: {total_answered}/{total_correct}"
        )
        
        return Response({
            **evaluation,
            'total_answered': total_answered,
            'total_correct': total_correct
        })
        
    except Exception as e:
        logger.error(f"Failed to submit MCQ answer: {str(e)}")
        return Response({
            'error': f'Failed to submit answer: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_objective_questions(request, session_id):
    try:
        session = get_object_or_404(CandidateSession, session_id=session_id)
        
        if not session.tech_stack:
            return Response({
                'error': 'No tech stack found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mcq_service = get_mcq_service()
        questions, metadata = mcq_service.generate_objective_questions(
            tech_stack=session.tech_stack,
            experience_level=session.experience_level or "mid"
        )
        
        session.objective_questions = questions
        session.save()
        
        logger.info(f"Generated {len(questions)} objective questions for session {session_id}")
        
        return Response({
            'objective_questions': questions
        })
        
    except Exception as e:
        logger.error(f"Failed to generate objective questions: {str(e)}")
        return Response({
            'error': f'Failed to generate questions: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_objective_answer(request, session_id):
    try:
        session = get_object_or_404(CandidateSession, session_id=session_id)
        
        question_index = request.data.get('question_index')
        user_answer = request.data.get('answer')
        
        if question_index is None or not user_answer:
            return Response({
                'error': 'Missing required fields: question_index, answer'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if question_index >= len(session.objective_questions):
            return Response({
                'error': 'Invalid question index'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        question = session.objective_questions[question_index]
        
        # Evaluate using LLM
        mcq_service = get_mcq_service()
        evaluation, metadata = mcq_service.evaluate_objective_answer(
            question=question,
            user_answer=user_answer
        )
        
        # Store evaluation
        if not session.objective_evaluations:
            session.objective_evaluations = []
        session.objective_evaluations.append(evaluation)
        session.save()
        
        logger.info(
            f"Objective answer evaluated for session {session_id}. "
            f"Score: {evaluation.get('score', 0)}"
        )
        
        return Response(evaluation)
        
    except Exception as e:
        logger.error(f"Failed to evaluate objective answer: {str(e)}")
        return Response({
            'error': f'Failed to evaluate answer: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def calculate_skill_ratings(request, session_id):
    try:
        session = get_object_or_404(CandidateSession, session_id=session_id)
        
        if not session.mcq_answers:
            return Response({
                'error': 'No MCQ answers found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mcq_service = get_mcq_service()
        skill_ratings = {}
        
        for skill, mcq_results in session.mcq_answers.items():
            # Find relevant objective evaluations
            relevant_objectives = []
            for i, question in enumerate(session.objective_questions or []):
                if question.get('focus_skill') == skill:
                    if i < len(session.objective_evaluations or []):
                        relevant_objectives.append(session.objective_evaluations[i])
            
            # Calculate rating
            rating = mcq_service.calculate_skill_rating(
                mcq_results=mcq_results,
                objective_evaluations=relevant_objectives if relevant_objectives else None
            )
            
            skill_ratings[skill] = rating
        
        # Store ratings
        session.skill_ratings = skill_ratings
        
        # Transition to closing phase if all assessments are complete
        from talent_scout.models import InterviewPhase
        if session.current_phase == InterviewPhase.TECHNICAL_SCREENING:
            # Check if both MCQ and objective assessments are done
            has_mcq_answers = bool(session.mcq_answers)
            has_objective_answers = bool(session.objective_evaluations)
            
            # If we're calculating ratings, it means the assessment is complete
            if has_mcq_answers:
                session.current_phase = InterviewPhase.CLOSING
                session.is_active = False
                from django.utils import timezone
                session.completed_at = timezone.now()
                logger.info(f"Session {session_id} transitioned to CLOSING phase")
        
        session.save()
        
        logger.info(f"Calculated skill ratings for session {session_id}: {skill_ratings}")
        
        return Response({
            'skill_ratings': skill_ratings
        })
        
    except Exception as e:
        logger.error(f"Failed to calculate ratings: {str(e)}")
        return Response({
            'error': f'Failed to calculate ratings: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def download_pdf_report(request, session_id):
    try:
        session = get_object_or_404(CandidateSession, session_id=session_id)
        
        # Generate assessment summary using Groq
        groq_service = get_groq_service()
        
        summary_prompt = f"""Generate a professional assessment summary for a technical interview.

Candidate: {session.full_name or 'Candidate'}
Position: {session.position_applied or 'Not specified'}
Experience: {session.experience_level or 'Not specified'}

Skills Tested: {', '.join(session.tech_stack or [])}

Skill Ratings:
{json.dumps(session.skill_ratings or {}, indent=2)}

Write a 2-3 paragraph professional summary highlighting:
1. Overall technical competency level
2. Key technical strengths demonstrated
3. Areas that may need further development
4. Hiring recommendation (Highly Recommended / Recommended / Consider / Not Recommended)

Be constructive, professional, and specific."""

        try:
            summary, _ = groq_service.chat_completion(
                system_prompt="You are an experienced technical recruiter writing candidate assessments.",
                user_message=summary_prompt,
                temperature=0.7
            )
        except Exception as e:
            logger.warning(f"Failed to generate LLM summary: {e}. Using fallback.")
            summary = f"""Based on the technical screening, {session.full_name or 'the candidate'} has demonstrated competency across the evaluated skills. The assessment shows a solid understanding of the required technologies for the {session.position_applied or 'position'} role. Further interview rounds are recommended to assess cultural fit and project experience."""
        
        # Prepare candidate data
        candidate_data = {
            'full_name': session.full_name or 'Candidate',
            'email': session.email or 'Not provided',
            'phone': session.phone or 'Not provided',
            'location': session.location or 'Not specified',
            'experience_level': session.experience_level or 'Not specified',
            'position_applied': session.position_applied or 'Not specified',
            'years_experience': session.years_experience or 0
        }
        
        # Generate PDF
        pdf_generator = get_pdf_generator()
        pdf_buffer = pdf_generator.generate_report(
            candidate_data=candidate_data,
            skill_ratings=session.skill_ratings or {},
            assessment_summary=summary,
            logo_path=None  # Add logo path if available
        )
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        filename = f"screening_report_{session.full_name or 'candidate'}".replace(' ', '_')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        
        logger.info(f"Generated PDF report for session {session_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate PDF report: {str(e)}")
        return Response({
            'error': f'Failed to generate report: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
