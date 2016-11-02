#from pydub import AudioSegment
#AudioSegment.from_mp3("test.mp3")
#dic = []
#for item in range(1,10):
#    dic['ABC'+str(item)] = item
#dic['ABC3'] = '33'
#dic['ABC3'] = '333'
#print dic
map1 = tuple((('ABC3',1),('ABC3',2),('ABC3',3),('ABC3',5),('ABC3',6)))
print map1

songs = [item for item in map1 if item[0]=='ABC3']
print songs