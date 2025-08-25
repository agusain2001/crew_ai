#!/usr/bin/env python3
"""
CrewAI SEO Analysis and Recommendation System
A comprehensive SEO analysis tool using CrewAI, Google Gemini, and BrightData
"""

import os
import sys
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

# CrewAI imports
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('seo_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SEOAnalysisSystem:
    """Main SEO Analysis System using CrewAI"""
    
    def __init__(self):
        """Initialize the SEO Analysis System"""
        self.setup_environment()
        self.setup_llm()
        self.setup_tools()
        self.setup_agents()
        self.setup_tasks()
        self.setup_crew()
        
    def setup_environment(self):
        """Setup environment variables and configuration"""
        # Ensure API keys are available
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.bright_data_api_key = os.getenv('BRIGHT_DATA_API_KEY')
        
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        if not self.serper_api_key:
            raise ValueError("SERPER_API_KEY environment variable is required")
        if not self.bright_data_api_key:
            raise ValueError("BRIGHT_DATA_API_KEY environment variable is required")
            
        logger.info("Environment variables configured successfully")
        
    def setup_llm(self):
        """Setup Google Gemini LLM via LiteLLM"""
        try:
            self.llm = LLM(
                model="gemini/gemini-1.5-flash",
                api_key=self.gemini_api_key,
                temperature=0.1,
                max_tokens=4000
            )
            logger.info("Google Gemini LLM configured successfully")
        except Exception as e:
            logger.error(f"Failed to setup LLM: {e}")
            raise
            
    def setup_tools(self):
        """Setup tools for web scraping and search"""
        try:
            # Web scraping tool
            self.scrape_tool = ScrapeWebsiteTool()
            
            # Search tool for SEO research
            self.search_tool = SerperDevTool(api_key=self.serper_api_key)
            
            logger.info("Tools configured successfully")
        except Exception as e:
            logger.error(f"Failed to setup tools: {e}")
            raise
            
    def setup_agents(self):
        """Setup CrewAI agents for SEO analysis"""
        
        # SEO Researcher Agent
        self.seo_researcher = Agent(
            role='SEO Research Specialist',
            goal='Extract and analyze comprehensive SEO data from websites',
            backstory="""You are an expert SEO researcher with deep knowledge of 
            search engine optimization best practices. You specialize in analyzing 
            website content, structure, and technical SEO elements to identify 
            optimization opportunities.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.scrape_tool, self.search_tool],
            llm=self.llm,
            max_iter=3,
            memory=True
        )
        
        # Content Strategist Agent
        self.content_strategist = Agent(
            role='SEO Content Strategist',
            goal='Analyze content and provide strategic SEO recommendations',
            backstory="""You are a seasoned content strategist with expertise in 
            SEO content optimization. You understand how to align content with 
            search intent, optimize for keywords, and improve user engagement 
            metrics that impact search rankings.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.search_tool],
            llm=self.llm,
            max_iter=3,
            memory=True
        )
        
        # Technical SEO Analyst Agent
        self.technical_analyst = Agent(
            role='Technical SEO Analyst',
            goal='Analyze technical SEO aspects and provide optimization recommendations',
            backstory="""You are a technical SEO expert who specializes in 
            website performance, crawlability, indexability, and technical 
            optimization factors that impact search engine rankings.""",
            verbose=True,
            allow_delegation=False,
            tools=[self.scrape_tool],
            llm=self.llm,
            max_iter=3,
            memory=True
        )
        
        # Report Generator Agent
        self.report_generator = Agent(
            role='SEO Report Specialist',
            goal='Compile comprehensive SEO analysis reports with actionable recommendations',
            backstory="""You are an expert at synthesizing complex SEO data into 
            clear, actionable reports. You excel at prioritizing recommendations 
            based on impact and effort, and presenting findings in a way that 
            both technical and non-technical stakeholders can understand.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=2,
            memory=True
        )
        
        logger.info("Agents configured successfully")
        
    def setup_tasks(self):
        """Setup tasks for the SEO analysis workflow"""
        
        # Task 1: Website Data Extraction
        self.extraction_task = Task(
            description="""
            Extract comprehensive SEO data from the provided URL: {url}
            
            Your analysis should include:
            1. Page title and meta description
            2. Header structure (H1, H2, H3, etc.)
            3. Content analysis (word count, keyword density)
            4. Internal and external links
            5. Image alt tags and optimization
            6. URL structure and parameters
            7. Page loading speed indicators
            8. Mobile responsiveness indicators
            9. Schema markup presence
            10. Social media meta tags
            
            Provide detailed findings for each element analyzed.
            """,
            expected_output="""
            A comprehensive JSON-formatted report containing:
            - Page metadata (title, description, keywords)
            - Content structure analysis
            - Technical SEO elements
            - Link analysis
            - Performance indicators
            - Identified issues and opportunities
            """,
            agent=self.seo_researcher,
            tools=[self.scrape_tool, self.search_tool]
        )
        
        # Task 2: Content Strategy Analysis
        self.content_analysis_task = Task(
            description="""
            Based on the extracted website data, perform a comprehensive content analysis:
            
            1. Keyword analysis and optimization opportunities
            2. Content quality and relevance assessment
            3. Search intent alignment evaluation
            4. Content gap identification
            5. Competitor content analysis (search for similar content)
            6. Content structure and readability assessment
            7. User engagement optimization suggestions
            8. Content freshness and update recommendations
            
            Focus on actionable insights that can improve search rankings.
            """,
            expected_output="""
            A detailed content strategy report including:
            - Keyword optimization recommendations
            - Content quality assessment
            - Search intent analysis
            - Content gap opportunities
            - Competitor insights
            - Actionable improvement suggestions
            """,
            agent=self.content_strategist,
            context=[self.extraction_task]
        )
        
        # Task 3: Technical SEO Analysis
        self.technical_analysis_task = Task(
            description="""
            Perform a technical SEO analysis based on the extracted data:
            
            1. Page speed and performance analysis
            2. Mobile-friendliness assessment
            3. URL structure optimization
            4. Internal linking structure evaluation
            5. Schema markup recommendations
            6. Crawlability and indexability assessment
            7. Security and HTTPS implementation
            8. Core Web Vitals considerations
            9. Technical error identification
            10. Site architecture recommendations
            
            Prioritize recommendations based on SEO impact.
            """,
            expected_output="""
            A technical SEO analysis report containing:
            - Performance optimization recommendations
            - Mobile optimization suggestions
            - Technical issue identification
            - Schema markup opportunities
            - Site architecture improvements
            - Priority-ranked action items
            """,
            agent=self.technical_analyst,
            context=[self.extraction_task]
        )
        
        # Task 4: Comprehensive Report Generation
        self.report_task = Task(
            description="""
            Compile all analysis findings into a comprehensive SEO audit report:
            
            1. Executive summary with key findings
            2. Current SEO performance assessment
            3. Priority recommendations (High, Medium, Low impact)
            4. Technical improvements needed
            5. Content optimization opportunities
            6. Competitive positioning insights
            7. Implementation timeline suggestions
            8. Expected impact and ROI estimates
            9. Monitoring and measurement recommendations
            10. Next steps and action plan
            
            Make the report actionable and easy to understand for both technical and business stakeholders.
            """,
            expected_output="""
            A comprehensive SEO audit report in markdown format containing:
            - Executive Summary
            - Current State Analysis
            - Priority Recommendations Matrix
            - Technical Improvements
            - Content Strategy
            - Implementation Roadmap
            - Success Metrics
            - Conclusion and Next Steps
            """,
            agent=self.report_generator,
            context=[self.extraction_task, self.content_analysis_task, self.technical_analysis_task],
            output_file="seo_analysis_report.md"
        )
        
        logger.info("Tasks configured successfully")
        
    def setup_crew(self):
        """Setup the CrewAI crew with all agents and tasks"""
        try:
            self.crew = Crew(
                agents=[
                    self.seo_researcher,
                    self.content_strategist,
                    self.technical_analyst,
                    self.report_generator
                ],
                tasks=[
                    self.extraction_task,
                    self.content_analysis_task,
                    self.technical_analysis_task,
                    self.report_task
                ],
                process=Process.sequential,
                verbose=True,
                memory=True,
                planning=True,
                planning_llm=self.llm
            )
            logger.info("CrewAI crew configured successfully")
        except Exception as e:
            logger.error(f"Failed to setup crew: {e}")
            raise
            
    def analyze_website(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive SEO analysis on the provided URL
        
        Args:
            url (str): The website URL to analyze
            
        Returns:
            Dict[str, Any]: Analysis results and report
        """
        try:
            logger.info(f"Starting SEO analysis for: {url}")
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Execute the crew
            result = self.crew.kickoff(inputs={'url': url})
            
            logger.info("SEO analysis completed successfully")
            
            return {
                'status': 'success',
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'result': result,
                'report_file': 'seo_analysis_report.md'
            }
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            return {
                'status': 'error',
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

def main():
    """Main function to run the SEO analysis"""
    try:
        # Initialize the SEO analysis system
        seo_system = SEOAnalysisSystem()
        
        # Get URL from command line or prompt user
        if len(sys.argv) > 1:
            url = sys.argv[1]
        else:
            url = input("Enter the website URL to analyze: ").strip()
            
        if not url:
            print("Error: No URL provided")
            sys.exit(1)
            
        print(f"Starting SEO analysis for: {url}")
        print("This may take several minutes...")
        
        # Perform analysis
        result = seo_system.analyze_website(url)
        
        # Display results
        if result['status'] == 'success':
            print("\n" + "="*50)
            print("SEO ANALYSIS COMPLETED SUCCESSFULLY")
            print("="*50)
            print(f"URL Analyzed: {result['url']}")
            print(f"Timestamp: {result['timestamp']}")
            print(f"Report saved to: {result['report_file']}")
            print("\nCheck the generated report file for detailed findings and recommendations.")
        else:
            print("\n" + "="*50)
            print("SEO ANALYSIS FAILED")
            print("="*50)
            print(f"URL: {result['url']}")
            print(f"Error: {result['error']}")
            
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

