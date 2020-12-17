#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 18:04:33 2020

@author: macuser
"""
import datetime
from notion.client import NotionClient
from notion.collection import NotionDate

PERIODICITY_DUE_DICT = {'Daily': 1,
                    '3t/w': 2,
                    '2t/w': 3,
                    '1t/w': 7,
                    '1t/2w': 14, 
                    '2t/m': 15,
                    '1t/m': 30,
                    '1t/2m': 60, 
                    '1t/3m': 90
    }

PERIODICITY_SET_DICT = {'/w': 1,
                        '/m': 7,
                        '/2m': 14,
                        '/3m':14
    }


client = NotionClient(token_v2='6fbfb3606dbe98bc33276b43adc67c82b3f98a4cfe6ce13fb1d9695ea7dbb6be8655609124f2a1b6e9dbcf21f983e20066e68392a3832905d8a7d3486796085f80859d8baa7c0b8f478e30bd9d6c')
page = client.get_block("https://www.notion.so/Test-task-figured-out-4a3c87d8f25f429b9b350567d4705191")
today = datetime.date.today()


for child in page.children:
    block_type = child.get("type")
    if block_type == 'collection_view':
        collection_id = child.collection.id
        

#get the lines we need to work with        
items = client.get_collection(collection_id)
collection_rows = items.get_rows()

#create a DONE_list to work with
list_of_tasks = [] 
for row in collection_rows:
    if row.get_all_properties()['status'] == 'DONE':
        list_of_tasks.append(row)
        
#checking the status of tasks in 'DONE':
for task in list_of_tasks:
    flag = False
    set_date = task.get_all_properties()['set_date'].start
    due_date = task.get_all_properties()['due_date'].start
    
    if set_date > today:
        continue
    
    elif set_date < today:
        periodicity = task.get_all_properties()['periodicity']
        for i in periodicity:
            if '/' in i or i == 'Daily':
                
                #calculate new_due_date
                added_due_date = PERIODICITY_DUE_DICT[i]
                due_delta = datetime.timedelta(days=added_due_date)
                new_due_date = due_date + due_delta
                task.set_property('due_date', NotionDate(new_due_date)) 
                
                #calculate new set_date
                if i == 'Daily':
                    task.set_property('set_date', NotionDate(due_date))
                else:
                    sub_set_date = PERIODICITY_SET_DICT[i[2:]]
                    set_delta = datetime.timedelta(days=sub_set_date)
                    new_set_date = due_date - set_delta
                    task.set_property('set_date', NotionDate(new_set_date)) 
    else:
        task.set_property('status', 'TO DO')
        
        