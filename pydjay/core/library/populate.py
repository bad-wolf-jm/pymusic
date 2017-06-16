from pydjay.library import init, load_file, save
import os
from PIL import Image
import sys
import io

_root_folder = '/Users/jihemme/.pydjay'
init('/Users/jihemme/.pydjay')


scan_root = sys.argv[1]

if not os.path.exists(scan_root):
    sys.exit(1)


db = {}
    
for f in os.listdir(scan_root):
    f = os.path.join(scan_root, f)
    print f
    track = load_file(f)
    if not track:
        continue
    if track.metadata.album_cover is not None:
        cover = track.metadata.album_cover
        im_type = cover[0]
        im_data = cover[1]
        ext = {'image/jpeg': 'jpg','image/png': 'png'}.get(im_type, None)
        if ext is not None:
            data = io.BytesIO(im_data)
            image = Image.open(data)
            cover_art_data = {}
            image.save(os.path.join('/Users/jihemme/.pydjay/image_cache', 'original_'+str(track)+".png"))
            cover_art_data['original'] = os.path.join('/Users/jihemme/.pydjay/image_cache', 'original_'+str(track)+".png")
            image.thumbnail((320,320), Image.ANTIALIAS)
            image.save(os.path.join('/Users/jihemme/.pydjay/image_cache', 'medium_'+str(track)+".png"))
            cover_art_data['medium'] = os.path.join('/Users/jihemme/.pydjay/image_cache', 'medium_'+str(track)+".png")
            image.thumbnail((160,160), Image.ANTIALIAS)
            image.save(os.path.join('/Users/jihemme/.pydjay/image_cache', 'small_'+str(track)+".jpg"))
            cover_art_data['small'] = os.path.join('/Users/jihemme/.pydjay/image_cache', 'small_'+str(track)+".png")
            image.thumbnail((100,100), Image.ANTIALIAS)
            image.save(os.path.join('/Users/jihemme/.pydjay/image_cache', 'tiny_'+str(track)+".jpg"))
            cover_art_data['tiny'] = os.path.join('/Users/jihemme/.pydjay/image_cache', 'tiny_'+str(track)+".png")
            track.metadata.album_cover = cover_art_data
            #im   = CoreImage(data, ext = ext)
            #self._album_art = im
    db[f] = track


import json

if _root_folder is not None:
    foo = open(os.path.join(_root_folder, "library2.data"), "w")
    tracks = [(key, _library[key].location, _library[key].info._metadata, _library[key].metadata._metadata) for key in db]
    #print tracks
    db = json.dumps(tracks)
    foo.write(db)
    foo.close()
#save()