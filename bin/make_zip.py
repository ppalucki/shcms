import zipfile, os, sys, fnmatch
os.chdir('lib')
if os.path.isfile('lib.zip'):
    print 'removing lib.zip'
    os.remove('../app/lib.zip')
    
zf = zipfile.ZipFile('../app/lib.zip', 'w', zipfile.ZIP_DEFLATED)
for path, subfolders, filenames in os.walk('.'):
    for filename in filenames:
        fullpath = os.path.join(path, filename)
        if fnmatch.fnmatch(fullpath, '*.py'):
            print fullpath
            zf.write(fullpath)

print 'done.'
zf.close()
os.chdir('..')
            
            

    