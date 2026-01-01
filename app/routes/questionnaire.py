"""Questionnaire routes for financial health assessment"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, QuestionnaireResponse
from datetime import datetime

questionnaire_bp = Blueprint('questionnaire', __name__)


# Sample questionnaire questions
QUESTIONNAIRE = {
    'title': 'Financial Health Assessment',
    'description': 'Help us understand your financial situation to provide personalized insights.',
    'questions': [
        {
            'id': 'q1',
            'text': 'What is your current monthly revenue?',
            'type': 'numeric',
            'max_value': 1000000,
            'weight': 2,
            'unit': '$'
        },
        {
            'id': 'q2',
            'text': 'How many months of operating expenses do you have in cash reserves?',
            'type': 'numeric',
            'max_value': 12,
            'weight': 2,
            'unit': 'months'
        },
        {
            'id': 'q3',
            'text': 'What percentage of your invoices are paid within 30 days?',
            'type': 'numeric',
            'max_value': 100,
            'weight': 1.5,
            'unit': '%'
        },
        {
            'id': 'q4',
            'text': 'Do you have a formal budget in place?',
            'type': 'boolean',
            'weight': 1,
            'positive_answer': True
        },
        {
            'id': 'q5',
            'text': 'How often do you review your financial statements?',
            'type': 'multiple_choice',
            'weight': 1.5,
            'options': [
                {'value': 'daily', 'label': 'Daily', 'score': 100},
                {'value': 'weekly', 'label': 'Weekly', 'score': 80},
                {'value': 'monthly', 'label': 'Monthly', 'score': 60},
                {'value': 'quarterly', 'label': 'Quarterly', 'score': 40},
                {'value': 'annually', 'label': 'Annually or Less', 'score': 20}
            ]
        },
        {
            'id': 'q6',
            'text': 'What is your current debt-to-income ratio?',
            'type': 'multiple_choice',
            'weight': 2,
            'options': [
                {'value': 'below_25', 'label': 'Below 25%', 'score': 100},
                {'value': '25_50', 'label': '25-50%', 'score': 75},
                {'value': '50_75', 'label': '50-75%', 'score': 50},
                {'value': 'above_75', 'label': 'Above 75%', 'score': 25}
            ]
        },
        {
            'id': 'q7',
            'text': 'Do you use accounting software to track your finances?',
            'type': 'boolean',
            'weight': 1,
            'positive_answer': True
        },
        {
            'id': 'q8',
            'text': 'What is your average profit margin?',
            'type': 'numeric',
            'max_value': 100,
            'weight': 2,
            'unit': '%'
        }
    ]
}


@questionnaire_bp.route('/take', methods=['GET', 'POST'])
@login_required
def take_assessment():
    """Take or retake the financial health assessment."""
    if not current_user.is_verified:
        return redirect(url_for('auth.verify_email'))
    
    if request.method == 'POST':
        # Get answers from form
        answers = {}
        for question in QUESTIONNAIRE['questions']:
            q_id = question['id']
            q_type = question['type']
            
            if q_type == 'numeric':
                value = request.form.get(q_id, '')
                answers[q_id] = float(value) if value else 0
            elif q_type == 'boolean':
                answers[q_id] = request.form.get(q_id) == 'true'
            elif q_type == 'multiple_choice':
                answers[q_id] = request.form.get(q_id, '')
        
        # Calculate score
        score_data = calculate_financial_health_score(answers, QUESTIONNAIRE['questions'])
        
        # Save response
        response = QuestionnaireResponse(
            user_id=current_user.id,
            answers=answers,
            score=score_data['raw_score'],
            tier=score_data['tier']
        )
        
        db.session.add(response)
        db.session.commit()
        
        flash(f'Assessment complete! Your score: {score_data["raw_score"]:.1f}/100 - {score_data["tier"]}', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('questionnaire.html', questionnaire=QUESTIONNAIRE)


@questionnaire_bp.route('/api/questions')
@login_required
def get_questions():
    """API endpoint to get questionnaire questions (for AJAX)."""
    return jsonify(QUESTIONNAIRE)


def calculate_financial_health_score(answers, questions):
    """
    Calculate financial health score based on answers.
    
    Returns:
        dict: Contains raw_score, score_out_of_10, tier, and tier_description
    """
    total_score = 0
    total_weight = 0
    
    for question in questions:
        q_id = question['id']
        if q_id not in answers:
            continue
        
        answer = answers[q_id]
        weight = question['weight']
        question_type = question['type']
        
        if question_type == 'numeric':
            # Numeric questions: normalize to 0-100 scale
            max_value = question.get('max_value', 100)
            normalized = (answer / max_value) * 100 if max_value > 0 else 0
            score = min(100, normalized) * weight
        
        elif question_type == 'multiple_choice':
            # Find the score for the selected option
            selected_option = next(
                (opt for opt in question['options'] if opt['value'] == answer),
                None
            )
            score = (selected_option['score'] if selected_option else 0) * weight
        
        elif question_type == 'boolean':
            # Boolean questions: yes=100, no=0
            positive_answer = question.get('positive_answer', True)
            score = (100 if answer == positive_answer else 0) * weight
        else:
            score = 0
        
        total_score += score
        total_weight += weight
    
    # Calculate average score (0-100)
    raw_score = (total_score / total_weight) if total_weight > 0 else 0
    
    # Determine tier based on score
    if raw_score < 34:
        tier = 'Developing'
        tier_description = 'Building foundation'
    elif raw_score < 67:
        tier = 'Stable'
        tier_description = 'Solid foundation'
    else:
        tier = 'Optimized'
        tier_description = 'Excellent health'
    
    # Convert to 1-10 scale
    score_1_to_10 = min(10, max(1, int((raw_score / 10) + 0.5)))
    
    return {
        'raw_score': round(raw_score, 2),
        'score_out_of_10': score_1_to_10,
        'tier': tier,
        'tier_description': tier_description
    }
