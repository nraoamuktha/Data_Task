import scrapy
import json
import csv
import os
import networkx as nx
import matplotlib.pyplot as plt
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import random

class BusinessSpiderSpider(scrapy.Spider):
    name = "business_spider"
    allowed_domains = ["firststop.sos.nd.gov"]
    start_urls = ["https://firststop.sos.nd.gov/search/business"]

    def parse(self, response):
        payload = {"SEARCH_VALUE": "X", "STARTS_WITH_YN": "true", "ACTIVE_ONLY_YN": 'true'}
        return scrapy.http.JsonRequest(url="https://firststop.sos.nd.gov/api/Records/businesssearch", data=payload, callback=self.parse_businesses)

    def parse_businesses(self, response):
        json_response = json.loads(response.text)
        for company in json_response["rows"]:
            if json_response["rows"][company]["TITLE"][0][0] == "X":
                filtered_companies = scrapy.http.Request(
                    url=f"https://firststop.sos.nd.gov/api/FilingDetail/business/{company}/false", callback=self.get_other_agents)
                filtered_companies.cb_kwargs['company_name'] = json_response["rows"][company]["TITLE"][0]
                yield filtered_companies

    def get_other_agents(self, response, company_name):
        json_response = json.loads(response.text)
        drawer_details = json_response.get('DRAWER_DETAIL_LIST', [])
        commercial_agent, registered_agent, owners = "", "", ""
        for detail in drawer_details:
            if detail['LABEL'] == 'Commercial Registered Agent': commercial_agent = detail['VALUE']
            elif detail['LABEL'] == 'Registered Agent': registered_agent = detail['VALUE']
            elif detail['LABEL'] == 'Owner Name': owners = detail['VALUE']
        
        # Append to the CSV file in 'a' mode (since it's now cleared at the start)
        with open('business_details.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([company_name, commercial_agent, registered_agent, owners])

# Move graph generation outside the spider class
def create_graph():
    G = nx.Graph()
    # Reload the CSV file data to create the graph
    with open('business_details.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            company = row['company_name']
            commercial_agent = row['commercial_registered_agent']
            registered_agent = row['registered_agent']
            owner = row['owners']
            G.add_node(company, label='Company')  # Mark as company
            if commercial_agent: G.add_edge(company, commercial_agent)
            if registered_agent: G.add_edge(company, registered_agent)
            if owner: G.add_edge(company, owner)

    # Use a spring layout for better cluster visualization
    pos = nx.spring_layout(G, seed=42, k=1.0, iterations=200)  # Adjusted layout

    # Set up color maps for different clusters
    node_colors = [random.choice(['yellow', 'green', 'purple', 'cyan', 'blue']) for _ in G.nodes()]
    edge_colors = [random.choice(['blue', 'orange', 'green', 'red', 'purple']) for _ in G.edges()]

    plt.figure(figsize=(20, 20))  # Larger figure size

    # Draw the graph with the colored nodes and edges
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000, alpha=0.9)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, alpha=0.5)

    # Drawing the labels with a bounding box for better readability
    nx.draw_networkx_labels(G, pos, font_size=10, font_color='black', font_family='sans-serif', 
                            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'))

    plt.title("Companies, Registered Agents, and Owners (Improved Layout)")
    plt.axis('off')
    plt.savefig('improved_network_graph.png')
    plt.close()

# Function to run the spider and create the graph
def run_spider():
    # Clear the CSV file at the start
    with open('business_details.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['company_name', 'commercial_registered_agent', 'registered_agent', 'owners'])  # Write the header
    
    # Start the Scrapy spider
    process = CrawlerProcess(get_project_settings())
    process.crawl(BusinessSpiderSpider)
    process.start()

    # Once the crawling is finished, create the graph
    create_graph()

if __name__ == "__main__":
    run_spider()