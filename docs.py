import gdata.docs.service
import gdata.docs.client
import gdata.docs.data
import urllib

EMAIL='skicms@gmail.com'
PASSWORD='XXXX'

from BeautifulSoup import BeautifulSoup as BS
def pr(x): 
    print BS(unicode(x)).prettify()


client = gdata.docs.client.DocsClient(source='skicmsCO')
#client.ssl = True  # Force all API requests through HTTPS
client.http_client.debug = False  # Set to True for debugging HTTP requests
client.ClientLogin(EMAIL, PASSWORD, client.source)

feed = client.GetDocList()
feed = client.GetDocList(uri='/feeds/default/private/full?showfolders=true')
for entry in feed.entry:
    print entry.title.text.encode('UTF-8'), entry.GetDocumentType(), entry.resource_id.text
    # List folders the document is in.
    for folder in entry.InFolders():
        print ' *',folder.title

### copying
#duplicated_entry = client.Copy(source_entry, 'MyTwin')

# Tip: You can use the gdata.client.DocsClient.GetFileContent() method to return a 
# files contents in memory (rather than writing it to local disk). The examples below write the file to disk.
entry = client.GetDoc('document:1irGP6uYIQgK6zPEHWFilc4gSN4La8I5lb3LhPWIiGnM')
pr(client.get_file_content(entry.content.src
                              #, exportFormat='html', format='html'
                              ))

#f = entry.content.src+'&exportFormat=html&format=html'
#print urllib.urlopen(f).read()


# Retrieving a entry or resource again (with etAG)
#try:
#  doc = client.GetDoc('document%3A0AdkQLCU4KIBYZGZya2o4NGdfMTQ2NWhiemZjZ2M5', etag='"WEwVFBBDBSp7ImBr"')
#except gdata.client.NotModified, error:
#  print error

#from wx.py.PyShell import main; main(dict(globals(), ** locals()))



### low-level
#gd_client = gdata.docs.service.DocsService()
#gd_client.ClientLogin(email, password)
#print 'loading feed...'
#### all feed
#feed = gd_client.GetDocumentListFeed()

### folders feed
#query = gdata.docs.service.DocumentQuery(categories=['folder'], params={'showfolders': 'true'})
#feed = gd_client.Query(query.ToUri())

### Export
def export(resource_id, file_path):
    """Prompts that enable a user to download a local copy of a document."""
    file_name = os.path.basename(file_path)
    ext = 'HTML'
    content_type = gdata.docs.service.SUPPORTED_FILETYPES[ext]

    doc_type = resource_id[:resource_id.find(':')]

    # When downloading a spreadsheet, the authenticated request needs to be
    # sent with the spreadsheet service's auth token.
    print 'Downloading document to %s...' % (file_path,)
    self.gd_client.Export(resource_id, file_path)
    
