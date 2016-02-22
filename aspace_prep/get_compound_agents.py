from lxml import etree
import csv
import os
from os.path import join

def get_compound_agents(ead_dir, subjects_agents_dir):
    tags = ['persname','corpname','famname']
    uniques = []
    for filename in os.listdir(ead_dir):
        print "Extracting compound agents from {0}".format(filename)
        tree = etree.parse(join(ead_dir,filename))
        for agent in tree.xpath('//controlaccess/*'):
            if agent.tag in tags and agent.text is not None:
                agent_text = agent.text.strip().encode('utf-8')
                if '---' in agent_text:
                    agent_text = agent_text.replace('---','- --')
                if '--' in agent_text:
                    if agent_text not in uniques:
                        uniques.append(agent_text)

    data = []
    for unique in uniques:
        row = []
        row.append(unique)
        terms = unique.split('--')
        for term in terms:
            row.append(term)
        data.append(row)

    output_csv = join(subjects_agents_dir,'compound_agents.csv')
    if os.path.exists(output_csv):
        os.remove(output_csv)

    with open(output_csv, 'ab') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

def main():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aspace_ead_dir = join(project_dir, 'eads')
    subjects_agents_dir = join(project_dir,'subjects_agents')
    get_compound_agents(aspace_ead_dir, subjects_agents_dir)