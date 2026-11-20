import json,sys
Q={q['k']:q for q in json.load(open('/tmp/claude-0/tv/xpost/queue.json'))}
def info(k,net,dt):
    q=Q[k]; d={"autoPublish":True,"draft":False,"descendants":[],"hasNotReadNotes":False,"shortener":False,"smartLinkData":{"ids":[]},"mediaAltText":[],
      "publicationDate":{"dateTime":dt,"timezone":"America/Chicago"},"providers":[{"network":net}],"firstCommentText":q['fc'],"media":[q['media']]}
    if q['thumb']: d['videoThumbnailUrl']=q['thumb']
    if net=='youtube':
        d['text']=q['text']+' #shorts'
        d['youtubeData']={"title":q['yt_title'],"type":"short","privacy":"public","tags":["roblox","roblox story","storytime","in this town","fantasy","gaming"],"category":"GAMING","madeForKids":False,"isAiGeneratedContent":False}
    else:
        d['text']=q['text']
        d['tiktokData']={"privacyOption":"PUBLIC_TO_EVERYONE","title":q['tt_title'],"photoCoverIndex":0,"isAigc":True,"disableComment":False,"disableDuet":False,"disableStitch":False,"autoAddMusic":False,"commercialContentThirdParty":False,"commercialContentOwnBrand":False}
    return json.dumps(d,ensure_ascii=False)
for a in sys.argv[1:]:
    k,net,dt=a.split(',')
    print('###',k,net,dt); print(info(k,net,dt))
