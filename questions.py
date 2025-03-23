TECHNICAL_QUESTIONS = [
    "Tell me about a challenging technical problem you've solved recently.",
    "How do you handle tight deadlines and multiple competing priorities?",
    "Describe your experience with version control systems like Git.",
    "What's your approach to debugging complex issues?",
    "How do you stay updated with the latest technology trends?",
    "Tell me about a project you're most proud of and why.",
    "How do you handle disagreements with team members about technical decisions?",
    "What's your experience with agile development methodologies?",
    "How do you ensure code quality in your projects?",
    "Describe a situation where you had to learn a new technology quickly."
]

MEDICAL_QUESTIONS = [
    "Tell me about a challenging patient case you've handled recently.",
    "How do you manage stress in high-pressure medical situations?",
    "Describe your experience with electronic health records systems.",
    "How do you handle difficult conversations with patients or their families?",
    "What's your approach to staying current with medical research and guidelines?",
    "Tell me about a medical procedure you're most confident performing.",
    "How do you handle disagreements with colleagues about treatment plans?",
    "What's your experience with emergency situations?",
    "How do you ensure patient safety in your practice?",
    "Describe a situation where you had to make a quick medical decision."
]

def get_questions(field_id=None):
    """
    Returns a list of interview questions based on the selected field.
    If no field_id is provided, returns general interview questions.
    """
    if field_id is None:
        return [
            "Tell me about yourself and your background.",
            "What are your greatest strengths and weaknesses?",
            "Why are you interested in this position?",
            "Where do you see yourself in 5 years?",
            "Tell me about a challenging situation you faced and how you handled it.",
            "What is your greatest achievement?",
            "Why should we hire you?",
            "What are your salary expectations?",
            "Do you have any questions for us?",
            "What motivates you in your work?"
        ]
    
    questions = {
        1: [  # Technology
            "Tell me about your experience with modern programming languages and frameworks.",
            "How do you stay updated with the latest technology trends?",
            "Describe a challenging technical problem you've solved.",
            "What's your approach to debugging complex issues?",
            "How do you handle tight deadlines in software development?",
            "Tell me about your experience with agile methodologies.",
            "What's your preferred development environment and why?",
            "How do you ensure code quality in your projects?",
            "Describe your experience with version control systems.",
            "What's your strategy for learning new technologies?"
        ],
        2: [  # Finance
            "Walk me through your experience with financial modeling.",
            "How do you stay current with market trends?",
            "Describe your experience with risk assessment.",
            "What financial software tools are you proficient in?",
            "How do you handle high-pressure financial decisions?",
            "Tell me about your experience with financial reporting.",
            "What's your approach to portfolio management?",
            "How do you ensure compliance in financial operations?",
            "Describe your experience with financial forecasting.",
            "What strategies do you use for financial analysis?"
        ],
        3: [  # Healthcare
            "Tell me about your experience with patient care.",
            "How do you handle stressful medical situations?",
            "Describe your experience with healthcare regulations.",
            "What medical software systems are you familiar with?",
            "How do you maintain patient confidentiality?",
            "Tell me about your experience with medical documentation.",
            "What's your approach to patient communication?",
            "How do you stay updated with medical advancements?",
            "Describe your experience with healthcare protocols.",
            "What strategies do you use for patient education?"
        ],
        4: [  # Marketing
            "Walk me through your experience with digital marketing.",
            "How do you measure campaign success?",
            "Describe your experience with social media marketing.",
            "What marketing tools and platforms do you use?",
            "How do you develop marketing strategies?",
            "Tell me about your experience with content creation.",
            "What's your approach to brand management?",
            "How do you handle market research?",
            "Describe your experience with SEO.",
            "What strategies do you use for audience engagement?"
        ],
        5: [  # Education
            "Tell me about your teaching experience.",
            "How do you handle classroom management?",
            "Describe your experience with curriculum development.",
            "What educational technologies do you use?",
            "How do you assess student progress?",
            "Tell me about your experience with special education.",
            "What's your approach to student engagement?",
            "How do you handle parent communication?",
            "Describe your experience with educational programs.",
            "What strategies do you use for differentiated instruction?"
        ]
    }
    return questions.get(field_id, questions[1])  # Default to technology questions if field_id not found 