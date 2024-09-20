# Data_Task

### Business Scraper & Network Graph Generator

This repository contains a Python-based web scraper that collects business information from the North Dakota Secretary of State website. It utilizes Scrapy to extract data about companies, including their commercial registered agents, registered agents, and owners. After gathering the data, the repository includes code to generate a visual network graph that shows the relationships between these companies and their agents.

Table of Contents

	•	Usage
	•	Files
	•	Output

Usage

Running the Scraper

The scraper targets businesses in North Dakota whose names start with “X”. To run the scraper and generate the network graph:
          
          python business_spider.py

This will:

	1.	Scrape business information (Company name, Commercial Registered Agent, Registered Agent, and Owner) from the North Dakota Secretary of State website.
	2.	Store the data in business_data.csv.
	3.	Generate a graph based on the relationships between businesses and agents, saving it as Companies_Graph.png.

Output

After running the script:

	•	business_data.csv will be generated with the following columns:
	•	company_name: Name of the business
	•	commercial_registered_agent: Commercial registered agent for the business
	•	registered_agent: Registered agent for the business
	•	owners: Business owner(s)
	•	Companies_Graph.png: This image visualizes the relationships between businesses and their agents, as a network graph.

# Files

	•	business_spider.py: The main script for scraping business data and generating the graph.
	•	business_data.csv: A CSV file containing data collected from the web scraper.
	•	Companies_Graph.png: A PNG file representing the graph visualization of businesses and their agents.
	•	requirements.txt: A list of dependencies required to run the project.

# Output

The resulting graph (Companies_Graph.png) visualizes the relationships between companies, commercial registered agents, registered agents, and owners. Nodes in the graph represent businesses, and edges represent relationships with agents or owners.
