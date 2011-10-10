import pytassium
api_key=PROVIDE_YOUR_API_KEY
blacklisted_classes=['http://www.w3.org/2000/01/rdf-schema#Class','http://www.w3.org/1999/02/22-rdf-syntax-ns#Property',
'http://www.w3.org/2002/07/owl#Class','http://www.w3.org/2002/07/owl#DatatypeProperty', 'http://www.w3.org/2002/07/owl#ObjectProperty']
dataset = pytassium.Dataset('kasabi-directory',api_key)
response, data = dataset.select('''
PREFIX void:<http://rdfs.org/ns/void#> 
PREFIX dct: <http://purl.org/dc/terms/> 
SELECT ?t ?c ?count
WHERE{
  ?d a void:Dataset; void:classPartition ?p; dct:title ?t.
  ?p void:class ?c;
     void:entities ?count.
  FILTER(?count>'2')
} 
''')
if response.status in range(200,300):
  classes_dict = {}
  datasets_dict = {}
  for t in data[1]:
    d,c,count = str(t['t']),str(t['c']),int(t['count'])
    datasets_dict.setdefault(d,[]).append((c,count))
    classes_dict.setdefault(c,[]).append(d)
  #get a set of classes that appear in at least two datasets
  classes = [clazz for clazz,clazz_ds in classes_dict.items() if len(clazz_ds)>1 and not clazz in blacklisted_classes]
  result = {}
  for ds,ds_classes in datasets_dict.items():
    for clazz,count in ds_classes:
      if clazz in classes:
        result[(ds,clazz)] = count
  #get a list of unique datasets
  datasets = list(set([d for d,c in result.keys()]))
  datasets.sort()
  #sort classes according to the number of datasets they are used in. counts are computed previously
  classes.sort(key=lambda c:len(classes_dict[c]),reverse=True)
  #output data for protovis matrix
  print 'rows=['
  for ds in datasets:
    print '['
    for clazz in classes:
      print '"%s_%s_%d",' %(ds,clazz,result.get((ds,clazz),0))
    print '],'
  print '];'
  print 'classes=['
  for c in classes:
    print '"%s",' %c
  print '];'
  print 'datasets=['
  for d in datasets:
    print '"%s",' %d
  print '];'
else:
  print "Oh no! %d %s" % (response.status, response.reason)