import scrapy
import json
import csv
import networkx as nx
import matplotlib.pyplot as plt
import random
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

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
                yield scrapy.Request(
                    url=f"https://firststop.sos.nd.gov/api/FilingDetail/business/{company}/false", 
                    callback=self.get_other_agents, cb_kwargs={'company_name': json_response["rows"][company]["TITLE"][0]}
                )

    def get_other_agents(self, response, company_name):
        details = json.loads(response.text).get('DRAWER_DETAIL_LIST', [])
        agents = {"commercial": "", "registered": "", "owner": ""}
        for detail in details:
            if detail['LABEL'] == 'Commercial Registered Agent': agents["commercial"] = detail['VALUE']
            elif detail['LABEL'] == 'Registered Agent': agents["registered"] = detail['VALUE']
            elif detail['LABEL'] == 'Owner Name': agents["owner"] = detail['VALUE']
        with open('business_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([company_name, agents["commercial"], agents["registered"], agents["owner"]])

def create_graph():
    G = nx.Graph()
    with open('business_data.csv') as file:
        reader = csv.reader(file)
        for row in reader:
            G.add_node(row[0])
            if row[1]: G.add_edge(row[0], row[1])
            elif row[2]: G.add_edge(row[0], row[2])
            elif row[3]: G.add_edge(row[0], row[3])

    plt.figure(figsize=(18, 18))
    pos = nx.spring_layout(G)  
    for g in (G.subgraph(c) for c in nx.connected_components(G)):
        nx.draw_networkx(g, pos, node_size=40, node_color=[random.random()] * nx.number_of_nodes(g),
                         vmin=0.0, vmax=1.0, with_labels=True, font_size=3.5)
    plt.savefig('Companies_Graph.png', dpi=1000)

def run_spider():
    with open('business_data.csv', mode='w', newline='') as file:
        csv.writer(file).writerow(['company_name', 'commercial_registered_agent', 'registered_agent', 'owners'])
    process = CrawlerProcess(get_project_settings())
    process.crawl(BusinessSpiderSpider)
    process.start()
    create_graph()

if __name__ == "__main__":
    run_spider()