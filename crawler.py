import re
from selenium import webdriver
import time
import urllib.request
import os

driver = webdriver.PhantomJS(executable_path="D:/phantomjs.exe")
origin_path = r"./my_review__toefl_vocab.txt"
output_path = r"./VIDEO"

def click_n_geturl(find_idx):
    global html_code
    driver.find_elements_by_class_name(name="msg")[find_idx].click()
    time.sleep(3)
    html_code = driver.page_source
    video_url = re.search(r"http(.*).mp4",html_code)
    video_url = video_url.group()
    img_code = re.findall("img\.iwordshow\.com\/snapshot\/(.*?)\?x-oss-process=style\/w3", html_code)
    img_code = img_code[find_idx]
    img_url = "http://img.iwordshow.com/snapshot/"+img_code
    return video_url, img_url

def extract_inf(word, load_idx=None):
    global html_code
    since = time.time()
    print("retrieving...")
    word_url = "http://www.91dub.com/search/%s?type=search" % (word.replace(" ", "%20"))
    driver.get(word_url)
    handles = driver.window_handles
    data = driver.find_elements_by_class_name("msg")
    
    _word = word.replace(" ","_")
    video_name = _word+"_video.mp4"
    img_name = _word+"_img.jpg"
    
    
    if(len(data) == 0): return None
    
    find_idx = None
    bup_idx = None
    find_txt = None
    bup_txt = None

    bup_res = re.search("((.*)\n)([\S\s]*)", data[0].text)
    bup_idx = 0
    bup_txt = bup_res.group()
    if (load_idx == None):
        for idx,blob in enumerate(data):
            #print(blob.text)
            res = re.search("([\S\s]*\n)((.*)\n)([\S\s]*)",blob.text)
            if(res != None):
                try:
                    find_idx = idx
                    find_txt = res.group()
                    video_url, img_url = click_n_geturl(find_idx)
                    print((video_url, img_url))
                    download(video_url, os.path.join(output_path, video_name))
                    download(img_url, os.path.join(output_path, img_name))
                    break
                except:
                    find_idx = None
                    find_txt = None
                    pass

        if(find_idx == None and bup_idx != None):
            try:
                find_idx = bup_idx
                find_txt = bup_txt
                video_url, img_url = click_n_geturl(find_idx)
                download(video_url, os.path.join(output_path, video_name))
                download(img_url, os.path.join(output_path, img_name))
            except:
                find_idx = None
                find_txt = None
                pass
    else:
        try:
            find_idx = load_idx
            find_txt = re.search("((.*)\n)([\S\s]*)", data[load_idx].text).group()
            video_url, img_url = click_n_geturl(find_idx)
            print((video_url, img_url))
            download(video_url, os.path.join(output_path, video_name))
            download(img_url, os.path.join(output_path, img_name))
        except:
            pass

    if(find_idx == None):
        return None
    
    time_elapsed = time.time() - since
    print('The code run {:.0f}m {:.0f}s'.format(time_elapsed // 60, time_elapsed % 60))
    print("-----------------------------")
    return video_url, video_name, img_url, img_name, find_txt

def download(url, output_path):
    urllib.request.urlretrieve(url,filename=output_path)

def format_wordlist(origin_path):
    with open(origin_path, encoding="utf-8") as f:
        txt = f.read()
    res = re.findall(u"<div class=\"\"section\"\"\"\"><br>\n([\S\s]*?)(\n)+", txt)
    output_str = ""
    word_list = []
    with open("./word_list.txt","w") as fw:
        for blob in res:
            word = re.search(r"\s.*\s", blob[0])
            word = word.group()[1:-1]
            word_list.append(word)
            fw.write(word+"\n")

    return word_list

def read_formatted_wordlist(origin_path):
    word_list = []
    with open(origin_path, encoding="utf-8") as f:
        for line in f.readlines():
            split_line = line.split(",")
            b = None if(len(split_line)==1) else int(split_line[1])-1
            tup = (split_line[0], b)
            word_list.append(tup)
    return word_list

if (__name__=="__main__"):
    #word_list = format_wordlist(origin_path)
    word_list = read_formatted_wordlist("./word_list.txt")
    anki_list = ""
    for word, load_idx  in word_list:
        ret_tuple = extract_inf(word, load_idx)
        if (ret_tuple == None): continue
        video_url, video_name, img_url, img_name, sentence = ret_tuple
        print(ret_tuple)
        sentence_arr = sentence.split("\n")
        if(len(sentence_arr)==2): sentence_arr.append("/")
        cur_item = word+"~"+video_name+"~"+img_name+"~"+sentence_arr[0]+"~"+sentence_arr[1]+"~"+sentence_arr[2]+"\n"
        anki_list += cur_item
    with open("./anki_list.txt", "w") as f:
        f.write(anki_list)