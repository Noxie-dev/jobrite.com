from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Job
from blog.models import BlogPost
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Populate the database with sample job listings and blog posts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate sample data...'))
        
        # Create sample jobs
        self.create_sample_jobs()
        
        # Create sample blog posts
        self.create_sample_blog_posts()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated sample data!'))

    def create_sample_jobs(self):
        """Create sample job listings for all categories"""
        
        # Call Center Jobs
        call_center_jobs = [
            {
                'title': 'Customer Service Representative',
                'company': 'TechSupport Solutions',
                'location': 'Remote',
                'job_type': 'full-time',
                'category': 'call-center',
                'description': 'Handle inbound customer calls, resolve issues, and provide excellent customer service. Work from home with flexible scheduling options.',
                'requirements': '• High school diploma or equivalent\n• Excellent communication skills\n• Basic computer skills\n• Quiet home office environment\n• Reliable internet connection',
                'salary_range': '$30,000 - $40,000',
                'is_remote': True,
                'is_featured': True,
            },
            {
                'title': 'Bilingual Call Center Agent',
                'company': 'Global Connect Services',
                'location': 'Austin, TX',
                'job_type': 'full-time',
                'category': 'call-center',
                'description': 'Provide customer support in English and Spanish. Handle billing inquiries, technical support, and account management.',
                'requirements': '• Fluent in English and Spanish\n• 1+ years customer service experience\n• Strong problem-solving skills\n• Ability to work in fast-paced environment',
                'salary_range': '$32,000 - $42,000',
                'is_remote': False,
                'is_featured': False,
            },
        ]  
      
        # Customer Care Jobs
        customer_care_jobs = [
            {
                'title': 'Customer Success Specialist',
                'company': 'CloudTech Inc',
                'location': 'Denver, CO',
                'job_type': 'full-time',
                'category': 'customer-care',
                'description': 'Build relationships with customers, ensure satisfaction, and drive retention. Work with cross-functional teams to improve customer experience.',
                'requirements': '• Bachelor\'s degree preferred\n• 2+ years customer service experience\n• CRM software experience\n• Strong analytical skills\n• Excellent written communication',
                'salary_range': '$45,000 - $55,000',
                'is_remote': False,
                'is_featured': True,
            },
            {
                'title': 'Remote Customer Care Associate',
                'company': 'E-commerce Plus',
                'location': 'Remote',
                'job_type': 'full-time',
                'category': 'customer-care',
                'description': 'Provide exceptional customer care via email, chat, and phone. Handle returns, exchanges, and product inquiries for online retail customers.',
                'requirements': '• High school diploma required\n• 1+ years retail or customer service experience\n• Proficient in Microsoft Office\n• Strong multitasking abilities\n• Home office setup required',
                'salary_range': '$35,000 - $45,000',
                'is_remote': True,
                'is_featured': False,
            },
        ]
        
        # Sales Jobs
        sales_jobs = [
            {
                'title': 'Inside Sales Representative',
                'company': 'SalesForce Pro',
                'location': 'Phoenix, AZ',
                'job_type': 'full-time',
                'category': 'sales',
                'description': 'Generate leads, qualify prospects, and close deals via phone and email. Work with warm leads and existing customer base to drive revenue growth.',
                'requirements': '• High school diploma required\n• 1+ years sales experience preferred\n• Strong communication and persuasion skills\n• Goal-oriented mindset\n• CRM experience a plus',
                'salary_range': '$40,000 - $60,000 + Commission',
                'is_remote': False,
                'is_featured': True,
            },
            {
                'title': 'Remote Sales Development Representative',
                'company': 'TechStart Solutions',
                'location': 'Remote',
                'job_type': 'full-time',
                'category': 'sales',
                'description': 'Identify and qualify potential customers through outbound prospecting. Schedule demos and meetings for senior sales team.',
                'requirements': '• Bachelor\'s degree preferred\n• Excellent phone and email communication\n• Experience with Salesforce or similar CRM\n• Self-motivated and results-driven\n• Tech industry interest',
                'salary_range': '$45,000 - $55,000 + Bonuses',
                'is_remote': True,
                'is_featured': False,
            },
        ]        

        # HR Jobs
        hr_jobs = [
            {
                'title': 'HR Coordinator',
                'company': 'People First Corp',
                'location': 'Seattle, WA',
                'job_type': 'full-time',
                'category': 'hr',
                'description': 'Support HR operations including recruitment, onboarding, and employee relations. Assist with benefits administration and compliance.',
                'requirements': '• Bachelor\'s degree in HR or related field\n• 1-2 years HR experience\n• Knowledge of employment law basics\n• Strong organizational skills\n• HRIS experience preferred',
                'salary_range': '$42,000 - $52,000',
                'is_remote': False,
                'is_featured': False,
            },
            {
                'title': 'Remote Recruiting Assistant',
                'company': 'Talent Acquisition Pro',
                'location': 'Remote',
                'job_type': 'full-time',
                'category': 'hr',
                'description': 'Support recruiting team with candidate sourcing, screening, and scheduling. Maintain applicant tracking system and assist with job postings.',
                'requirements': '• Associate degree or equivalent experience\n• Strong attention to detail\n• Excellent communication skills\n• Experience with job boards\n• ATS software knowledge a plus',
                'salary_range': '$38,000 - $48,000',
                'is_remote': True,
                'is_featured': False,
            },
        ]
        
        # IT Technician Jobs (Remote Mid-Level)
        it_jobs = [
            {
                'title': 'IT Support Technician',
                'company': 'TechSolutions Remote',
                'location': 'Remote',
                'job_type': 'full-time',
                'category': 'it',
                'description': 'Provide technical support to remote employees. Troubleshoot hardware and software issues, manage user accounts, and maintain IT documentation.',
                'requirements': '• Associate degree in IT or equivalent experience\n• 2-3 years technical support experience\n• Knowledge of Windows and Mac systems\n• Experience with remote support tools\n• Strong problem-solving skills',
                'salary_range': '$50,000 - $65,000',
                'is_remote': True,
                'is_featured': True,
            },
            {
                'title': 'Network Support Specialist',
                'company': 'CloudNet Systems',
                'location': 'Remote',
                'job_type': 'full-time',
                'category': 'it',
                'description': 'Monitor and maintain network infrastructure for remote clients. Perform network troubleshooting and implement security protocols.',
                'requirements': '• Bachelor\'s degree in IT or related field\n• 3+ years network administration experience\n• Cisco or CompTIA certifications preferred\n• Experience with VPN and firewall management\n• Available for on-call support',
                'salary_range': '$55,000 - $70,000',
                'is_remote': True,
                'is_featured': True,
            },
        ] 
       
        # Logistics Jobs (Remote Mid-Level)
        logistics_jobs = [
            {
                'title': 'Logistics Coordinator',
                'company': 'Supply Chain Solutions',
                'location': 'Remote',
                'job_type': 'full-time',
                'category': 'logistics',
                'description': 'Coordinate shipments, track inventory, and manage vendor relationships. Work with transportation partners to ensure timely deliveries.',
                'requirements': '• Bachelor\'s degree in Supply Chain or related field\n• 2-4 years logistics experience\n• Experience with WMS/TMS systems\n• Strong analytical and communication skills\n• Knowledge of shipping regulations',
                'salary_range': '$48,000 - $62,000',
                'is_remote': True,
                'is_featured': True,
            },
            {
                'title': 'Remote Inventory Analyst',
                'company': 'Global Logistics Inc',
                'location': 'Remote',
                'job_type': 'full-time',
                'category': 'logistics',
                'description': 'Analyze inventory levels, forecast demand, and optimize stock levels. Create reports and work with procurement team on purchasing decisions.',
                'requirements': '• Bachelor\'s degree in Business or related field\n• 3+ years inventory management experience\n• Advanced Excel skills\n• Experience with ERP systems\n• Strong attention to detail',
                'salary_range': '$52,000 - $68,000',
                'is_remote': True,
                'is_featured': False,
            },
        ]
        
        # Other Category Jobs
        other_jobs = [
            {
                'title': 'Virtual Assistant',
                'company': 'Executive Support Services',
                'location': 'Remote',
                'job_type': 'part-time',
                'category': 'other',
                'description': 'Provide administrative support to executives including calendar management, email handling, and project coordination.',
                'requirements': '• High school diploma required\n• 2+ years administrative experience\n• Proficient in Microsoft Office Suite\n• Excellent organizational skills\n• Reliable internet and quiet workspace',
                'salary_range': '$20 - $25 per hour',
                'is_remote': True,
                'is_featured': False,
            },
            {
                'title': 'Data Entry Specialist',
                'company': 'DataPro Services',
                'location': 'Miami, FL',
                'job_type': 'full-time',
                'category': 'other',
                'description': 'Accurately enter data into various systems and databases. Verify information and maintain data quality standards.',
                'requirements': '• High school diploma or equivalent\n• Fast and accurate typing skills (50+ WPM)\n• Attention to detail\n• Basic computer skills\n• Previous data entry experience preferred',
                'salary_range': '$28,000 - $35,000',
                'is_remote': False,
                'is_featured': False,
            },
        ]    
    
        # Combine all job categories
        all_jobs = (call_center_jobs + customer_care_jobs + sales_jobs + 
                   hr_jobs + it_jobs + logistics_jobs + other_jobs)
        
        # Create job instances
        created_count = 0
        for job_data in all_jobs:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=job_data['company'],
                defaults=job_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created job: {job.title} at {job.company}')
        
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} new job listings'))

    def create_sample_blog_posts(self):
        """Create sample blog posts for career advice section"""
        
        # Get or create a default author
        author, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@jobrite.com',
                'first_name': 'JobRite',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            author.set_password('admin123')
            author.save()
            self.stdout.write('Created admin user for blog posts')
        
        blog_posts = [
            {
                'title': '10 Essential Tips for Remote Job Interviews',
                'content': '''Remote job interviews have become the new standard in today's digital workplace. Whether you're interviewing for a customer service role, IT position, or sales job, these tips will help you succeed in your virtual interview.

**1. Test Your Technology**
Before the interview, test your camera, microphone, and internet connection. Ensure you have backup options like a mobile hotspot or phone number for audio-only backup.

**2. Create a Professional Environment**
Choose a quiet, well-lit space with a clean background. Remove distractions and inform household members about your interview time.

**3. Dress Professionally**
Dress as you would for an in-person interview. This helps you feel confident and shows respect for the interviewer.

**4. Prepare Your Materials**
Have your resume, portfolio, and notes easily accessible on your computer or printed nearby. Prepare questions about the role and company.

**5. Practice Common Remote Work Questions**
Be ready to discuss your home office setup, time management skills, and experience with remote collaboration tools.

**6. Show Enthusiasm for Remote Work**
Demonstrate your understanding of remote work challenges and your strategies for staying productive and connected.

**7. Maintain Eye Contact**
Look at the camera, not the screen, when speaking to simulate eye contact with your interviewer.

**8. Have Examples Ready**
Prepare specific examples of your achievements, problem-solving skills, and how you've handled challenges in previous roles.

**9. Ask Thoughtful Questions**
Inquire about team communication, performance expectations, and growth opportunities within the remote work environment.

**10. Follow Up Professionally**
Send a thank-you email within 24 hours, reiterating your interest and highlighting key points from the conversation.

Remember, remote interviews are an opportunity to showcase not just your qualifications, but also your ability to communicate effectively in a digital environment.''',
                'is_published': True,
            },   
         {
                'title': 'Building Your Career in Customer Service: A Complete Guide',
                'content': '''Customer service is one of the most accessible and rewarding career paths, offering opportunities for growth across industries. Whether you're starting in call centers or aiming for customer success roles, this guide will help you build a successful career.

**Starting Your Customer Service Journey**

Entry-level positions like Customer Service Representative or Call Center Agent provide excellent foundations. These roles teach essential skills:
- Communication and active listening
- Problem-solving under pressure
- Multi-tasking and time management
- Product knowledge and system navigation
- Conflict resolution and empathy

**Career Progression Paths**

1. **Specialist Track**: Customer Service Representative → Senior Representative → Team Lead → Supervisor
2. **Technical Track**: Support Agent → Technical Support Specialist → Support Engineer
3. **Success Track**: Customer Care Associate → Customer Success Specialist → Account Manager

**Essential Skills to Develop**

- **Communication**: Master both written and verbal communication across channels
- **Technology**: Learn CRM systems, help desk software, and communication tools
- **Analytics**: Understand metrics like CSAT, NPS, and resolution times
- **Industry Knowledge**: Develop expertise in your company's products and services

**Salary Expectations**

- Entry Level: $28,000 - $38,000
- Mid Level: $40,000 - $55,000
- Senior Level: $55,000 - $75,000+

**Remote Opportunities**

The customer service field offers excellent remote work opportunities. Many companies now hire remote customer service representatives, providing flexibility and eliminating commute time.

**Tips for Success**

1. Always maintain a positive attitude
2. Continuously learn about products and services
3. Seek feedback and act on it
4. Build relationships with team members
5. Look for process improvement opportunities

Customer service skills are transferable across industries, making this an excellent career choice for long-term growth and stability.''',
                'is_published': True,
            },
            {
                'title': 'The Rise of Remote Work: Opportunities in IT and Logistics',
                'content': '''The remote work revolution has opened unprecedented opportunities in IT and logistics. These traditionally office-based fields have adapted to distributed work models, creating new possibilities for professionals seeking flexibility.

**IT Remote Opportunities**

The IT sector leads in remote work adoption, with roles like:
- **IT Support Technician**: Provide remote technical support
- **Network Administrator**: Manage infrastructure remotely
- **Systems Analyst**: Analyze and improve IT systems
- **Cybersecurity Specialist**: Monitor and protect digital assets

**Key Skills for Remote IT Roles**
- Proficiency in remote access tools (VPN, RDP, TeamViewer)
- Strong troubleshooting and diagnostic skills
- Excellent written communication for ticket documentation
- Self-motivation and time management
- Continuous learning mindset for evolving technologies

**Logistics Goes Digital**

Modern logistics relies heavily on digital systems, enabling remote work in:
- **Supply Chain Coordination**: Manage vendor relationships and shipments
- **Inventory Analysis**: Forecast demand and optimize stock levels
- **Transportation Planning**: Route optimization and carrier management
- **Compliance Management**: Ensure regulatory adherence

**Essential Logistics Skills**
- Proficiency in WMS/TMS systems
- Data analysis and Excel expertise
- Understanding of shipping regulations
- Project management capabilities
- Strong attention to detail

**Salary Ranges**

**IT Positions:**
- IT Support Technician: $45,000 - $65,000
- Network Specialist: $55,000 - $75,000
- Systems Administrator: $60,000 - $85,000

**Logistics Positions:**
- Logistics Coordinator: $45,000 - $65,000
- Supply Chain Analyst: $50,000 - $70,000
- Transportation Manager: $60,000 - $85,000

**Getting Started**

1. **Build Technical Skills**: Invest in relevant certifications and training
2. **Gain Experience**: Start with entry-level positions to build expertise
3. **Develop Soft Skills**: Communication and problem-solving are crucial
4. **Create a Home Office**: Invest in reliable technology and workspace
5. **Network Professionally**: Join industry groups and online communities

The future of work is increasingly remote, and IT and logistics professionals are well-positioned to take advantage of this trend.''',
                'is_published': True,
            },           
 {
                'title': 'Mastering Sales: From Entry Level to Sales Success',
                'content': '''Sales offers one of the most lucrative and dynamic career paths available today. With the right approach, dedication, and skills, you can build a rewarding career that offers both financial success and personal growth.

**Understanding Sales Roles**

**Entry-Level Positions:**
- Sales Development Representative (SDR)
- Inside Sales Representative
- Customer Service Sales Associate
- Retail Sales Associate

**Mid-Level Positions:**
- Account Executive
- Sales Specialist
- Territory Manager
- Key Account Manager

**Senior-Level Positions:**
- Sales Manager
- Regional Sales Director
- VP of Sales
- Chief Revenue Officer

**Essential Sales Skills**

1. **Communication**: Master the art of listening and presenting
2. **Relationship Building**: Develop trust and rapport with clients
3. **Product Knowledge**: Become an expert in what you're selling
4. **Negotiation**: Learn to find win-win solutions
5. **Time Management**: Prioritize high-value activities
6. **Resilience**: Handle rejection and bounce back quickly

**The Sales Process**

- **Prospecting**: Identify potential customers
- **Qualifying**: Determine if prospects are good fits
- **Presenting**: Demonstrate value and benefits
- **Handling Objections**: Address concerns professionally
- **Closing**: Secure the commitment
- **Follow-up**: Maintain relationships and seek referrals

**Compensation Structure**

Sales roles typically offer:
- Base salary: $35,000 - $80,000+
- Commission: 10-50% of sales
- Bonuses: Performance and team incentives
- Benefits: Health, dental, retirement plans

**Remote Sales Opportunities**

Many sales roles now offer remote work options:
- Inside sales teams work entirely remotely
- Territory managers cover regions from home offices
- Account managers maintain client relationships virtually
- Sales development representatives prospect via phone and email

**Tips for Sales Success**

1. **Set Daily Goals**: Focus on activities that drive results
2. **Use CRM Effectively**: Track all interactions and opportunities
3. **Continuous Learning**: Stay updated on industry trends
4. **Network Actively**: Build professional relationships
5. **Seek Mentorship**: Learn from successful salespeople
6. **Celebrate Wins**: Acknowledge achievements, big and small

**Getting Started in Sales**

- Look for entry-level SDR or inside sales positions
- Consider industries you're passionate about
- Develop your communication and interpersonal skills
- Learn basic CRM and sales tools
- Practice your pitch and presentation skills

Sales is a merit-based field where hard work and results are rewarded. With dedication and the right approach, you can build a highly successful and fulfilling career.''',
                'is_published': True,
            },
            {
                'title': 'HR Career Paths: Building a Future in Human Resources',
                'content': '''Human Resources is a vital function in every organization, offering diverse career opportunities for people-focused professionals. From recruitment to employee development, HR careers provide the chance to make a meaningful impact on workplace culture and employee success.

**HR Career Progression**

**Entry Level:**
- HR Assistant
- Recruiting Coordinator
- Benefits Administrator
- HR Generalist

**Mid Level:**
- HR Business Partner
- Talent Acquisition Specialist
- Compensation Analyst
- Training and Development Specialist

**Senior Level:**
- HR Manager
- Director of Talent Acquisition
- VP of Human Resources
- Chief People Officer

**Core HR Functions**

1. **Recruitment and Talent Acquisition**
   - Sourcing and screening candidates
   - Conducting interviews and assessments
   - Managing the hiring process
   - Building talent pipelines

2. **Employee Relations**
   - Handling workplace conflicts
   - Ensuring policy compliance
   - Managing disciplinary actions
   - Promoting positive workplace culture

3. **Benefits and Compensation**
   - Designing compensation structures
   - Managing benefits programs
   - Conducting salary surveys
   - Ensuring pay equity

4. **Learning and Development**
   - Creating training programs
   - Managing performance reviews
   - Succession planning
   - Career development initiatives

**Essential HR Skills**

- **Communication**: Clear, empathetic, and professional interaction
- **Problem-Solving**: Address complex workplace issues
- **Confidentiality**: Handle sensitive information appropriately
- **Legal Knowledge**: Understand employment law and regulations
- **Technology**: Master HRIS, ATS, and other HR systems
- **Analytics**: Use data to make informed decisions

**Remote HR Opportunities**

Many HR functions can be performed remotely:
- Virtual recruiting and interviewing
- Remote employee onboarding
- Digital training and development
- Online performance management
- Virtual employee engagement initiatives

**Salary Expectations**

- HR Coordinator: $35,000 - $45,000
- HR Generalist: $45,000 - $60,000
- HR Business Partner: $65,000 - $85,000
- HR Manager: $75,000 - $100,000+

**Professional Development**

- **Certifications**: PHR, SHRM-CP, SHRM-SCP
- **Education**: Bachelor's in HR, Psychology, or Business
- **Networking**: Join SHRM and local HR associations
- **Continuous Learning**: Stay updated on employment law and best practices

**Getting Started in HR**

1. **Gain Experience**: Look for HR assistant or coordinator roles
2. **Develop People Skills**: Practice active listening and empathy
3. **Learn HR Systems**: Familiarize yourself with common HRIS platforms
4. **Understand Employment Law**: Take courses on workplace regulations
5. **Build Professional Network**: Connect with HR professionals

HR offers a rewarding career path for those passionate about helping people and organizations succeed. With the right skills and dedication, you can build a fulfilling career that makes a positive impact on workplace culture and employee satisfaction.''',
                'is_published': True,
            },
        ]   
     
        # Create blog post instances
        created_count = 0
        for post_data in blog_posts:
            post_data['author'] = author
            blog_post, created = BlogPost.objects.get_or_create(
                title=post_data['title'],
                defaults=post_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created blog post: {blog_post.title}')
        
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} new blog posts'))