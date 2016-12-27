# -*- coding: utf-8 -*-

import os
import sys
import json
import csv
import subprocess

# MADE WITH LOVE <3

entry_tempalte = '''
<div class="col-sm-6 col-md-4 el">
    <a style="display:block" href="{{prev}}{{link}}">
    <div class="portfolio-el view">
    <img src="../{{prev}}{{image_link}}" alt="project">
        <span class="mask">
            <div class="portfolio-middle">
                <h3 class="project-title br-bottom">{{title}}</h3>
                <p class="text">{{sub_title}}</p>
            </div>
        </a>
    </div>
    </a>
</div> 
'''


def call(command, show=False):
    '''
    calls shell with given command
    '''
    if show:
        print ">> "+command
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
    if result == "":
        pass
    else:
        print "OUT: " + result
    return result



def input_csv_to_json(csv_path):
    '''
    converts csv to json (actually a list, not json - fix func name)
    '''
    data = []
    with open(csv_path, 'rU') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            data.append(row)

    return data


def parse_teas(data):
    '''
    Parsed data from list to json
    '''
    json_data = {}
    
    # check if content dir in py folder exists
    if os.path.exists('content'):
        print 'delete content folder or file'
        return
    
    # make content and teas dirs
    os.mkdir('content')
    os.mkdir('content/teas/')
    
    
    # go through all teas
    for i, row in enumerate(data):
        if row[0] == "" or i == 0: # it is an empty row, skip it
            continue
        
        
        # replace all spaces with no spaces and split by '-' char
        catagories = row[1].strip().replace(' ', '').split('-')
        # keep track of current dictionary (key : value pairs)
        prev_dict = json_data
        # keep track of path
        path = 'teas/'
        # keep track of number of directroies 
        count = 2
        
        # create link for top level and how to get back to home (e.g. where ./index.html is)
        prev_dict['link'] = path + '%s.html' % 'teas'
        prev_dict['home'] = '../' 
        for j, c in enumerate(catagories): # go through catagories 
            if c == '':
                continue
            
            if c in prev_dict:  # if it already exists, switch to that and increment path and count
                prev_dict = prev_dict[c]
                path += '%s/' % c
                count += 1
            else: # otherwise create a new dictionary, make directory and add appropriate fields
                prev_dict[c] = {}
                path += '%s/' % c

                prev_dict[c]['link'] = path + '%s.html' % c
                prev_dict[c]['home'] = '../' * count
                prev_dict[c]['image_link'] = 'img/teas/' + c + '.jpg'

                prev_dict = prev_dict[c]

                os.mkdir('content/'+path)

                count += 1
                
            if len(catagories) -1 == j: # if we hit the last catagory (then tea is in this)
                tea = row[2]
                if 'teas' in prev_dict: # if the teas folder exists, don't create it
                    pass
                else: # create teas folder
                    prev_dict['teas'] = {}
                # add tea and appropriate fields from json file
                prev_dict['teas'][tea] = {}
                prev_dict['teas'][tea]['price'] = {}
                prev_dict['teas'][tea]['price']['50g'] = row[3]
                prev_dict['teas'][tea]['price']['100g'] = row[4]
                prev_dict['teas'][tea]['price']['250g'] = row[5]
                prev_dict['teas'][tea]['description'] = row[6]
                prev_dict['teas'][tea]['image_link'] = 'img/teas/' + tea + '.jpg'
                prev_dict['teas'][tea]['link'] = path + tea + '.html'
                prev_dict['teas'][tea]['home'] = '../' * count

            
                
    return json_data
                

def generate_pages(json_data, page_title):
    '''
    recusively goes through json file and creates catagory pages and tea pages
    '''
    create_catagory_page(json_data, page_title)
     
    for k,v in json_data.iteritems():
        if type(v) == dict and k != 'teas': #check if its a dictionary, don't do it for teas here
            generate_pages(v, page_title + ' / ' + k) # append the page title TODO: make it a link so they can go back.

def create_catagory_page(data, page_title):
    '''
    Creates pages for teas and catagories 
    '''
    
    # grab link, home, and image link for current catagory 
    if 'link' in data:
        link = data['link']
    else:
        link = None
        
    if 'home' in data:
        home = data['home']
    else:
        home = None
    
    if 'image_link' in data:
        image_link = data['image_link']
    else:
        image_link = None
    
    # copy the template into a new file
    call('cp catagory_template.html content/%s' % link)
    
    # replace prev with home, which should allow it to reference correct files (CSS, JS, other links)
    call("sed -i 's,{{prev}},%s,g' content/%s" % (home, link))
    
    entries = [] # holds entries for catagories 
    # print 'link: =', link
    # print 'home: =', home
    # print 'image_link = ', image_link 

    for k,v in data.iteritems(): # go through each catagory 
        if k == 'link' or k == 'home' or k == 'image_link' or k=='teas': # skip if these
            continue
        entry = entry_tempalte[:] # copy entry template from above
        
        
        entry = entry.replace('{{prev}}', home) # fix relative link
        v['image_link'] = '../img/black.jpg' # temp TODO: change it once better images found
        entry = entry.replace('{{image_link}}', v['image_link'])
        entry = entry.replace('{{title}}', k.replace('_', ' '))
        
        #print "v link", v['link']
        entry = entry.replace('{{link}}', v['link'])
        
        # grab sub catagories of the catagory
        if type(v) == dict:
            keys = ''
            for k2, v2 in v.iteritems():
                if k2 == 'link' or k2 == 'home' or k2 == 'image_link' or k2 == 'teas':
                    continue
                keys += (str(k2).replace('_', ' ')+', ')
            entry = entry.replace('{{sub_title}}', keys[:-2])
        entries.append(entry)
    
        
    teas = []

    ########## teas ##########
    if type(v) == dict and 'teas' in data:
        #print "############### tea #####################"
        # grab the teas of the catagory 
        for kt, vt in data['teas'].iteritems():
            
            thome = vt['home']
            tlink = vt['link'].replace(' ', '_')
            
            tea_entry = entry_tempalte[:]
            tea_entry = tea_entry.replace('{{prev}}', home)
            
            
            if os.path.exists('../'+vt['image_link'].replace(' ', '_')):
                #print vt['image_link']
                pass
            else:
                vt['image_link'] = '../img/comingsoon.jpg' # temp
                
            
            tea_entry = tea_entry.replace('{{image_link}}', vt['image_link'].replace(' ', '_'))
            tea_entry = tea_entry.replace('{{title}}', kt)
            tea_entry = tea_entry.replace('{{sub_title}}', vt['description'])
            tea_entry = tea_entry.replace('{{link}}', tlink)
            tea_entry = tea_entry.replace('{{prev}}', home)

            teas.append(tea_entry)
            
            
            call('cp tea_template.html content/%s' % tlink)
            
            
            
            call("sed -i 's,{{prev}},%s,g' content/%s" % (home, tlink))
            call("sed -i 's,{{title}},%s,g' content/%s" % (kt, tlink))
            call("sed -i 's,{{name}},%s,g' content/%s" % (kt, tlink))
            call("sed -i 's,{{sub_title}},%s,g' content/%s" % (' ', tlink))
            call("sed -i 's,{{image_link}},%s,g' content/%s" % (vt['image_link'].replace(' ', '_'), tlink))

            #print "-------", vt['description']
            #call("sed -i 's?{{description}}?%s?g' content/%s" % (vt['description'], tlink))
            
            with open(os.path.join('content/', str(tlink)), 'r') as tinfile:
                tfiledata=tinfile.read()
        
            with open(os.path.join('content/', tlink), 'w') as toutfile:
                tfiledata = tfiledata.replace('{{description}}', vt['description'])
                
                fiftyg = vt['price']['50g'].replace('.', ',')
                onekg = vt['price']['100g'].replace('.', ',')
                twofiftyg = vt['price']['250g'].replace('.', ',')
                
                if fiftyg != "":
                    fiftyg = '€'+fiftyg
                else:
                    fiftyg = 'NA'
                
                if onekg != "":
                    onekg = '€'+onekg
                else:
                    onekg = 'NA'
                    
                if twofiftyg != "":
                    twofiftyg = '€'+twofiftyg
                else:
                    twofiftyg = 'NA'
                    
                
                tfiledata = tfiledata.replace('{{50g}}', fiftyg)
                tfiledata = tfiledata.replace('{{100g}}', onekg)
                tfiledata = tfiledata.replace('{{250g}}', twofiftyg)
                toutfile.write(tfiledata)
            
            
            
        #print ('############## end tea ##################')

    #########################
        
    
    
    str_entries = ''
    for e in entries:
        str_entries += e + '\n'
        
    for te in teas:
        str_entries += te + '\n'
    
    with open('content/'+link, 'r') as infile:
        filedata=infile.read()
        
    with open('content/'+link, 'w') as outfile:
        filedata = filedata.replace('{{title}}', page_title.replace('_', ' '))
        filedata = filedata.replace('{{sub_title}}', '')
        outfile.write(filedata.replace('{{entries}}', str_entries))

    #call("sed -i 's?{{entries}}?%s?g' content/%s" % (str_entries, link))
    
    
    

def write_json_file(path, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

if __name__ == '__main__':
    path = 'teas.csv'
    call('rm -rf content')
    data = input_csv_to_json(path)
    json_data = parse_teas(data)
    write_json_file('teas.json', json_data)
    generate_pages(json_data, 'Alle Tees')
    print 'done'
    
