from django import template
import re
from django.template.loader_tags import BlockNode

from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode

register = template.Library()
	
@register.tag
def box(parser, token):
	title_nodelist = template.NodeList()
	bits = re.findall(r'"[^"]+"|\b[^"]+\b[^"]', token.contents) # supports spaces in quotation marks eg. "Hello world" 
    
	if len(bits) < 2:
		raise template.TemplateSyntaxError("'%s, %s' tag takes at least one arguments" % (bits[0]))
    
	nodelist = parser.parse(('title', 'endbox'))
	token = parser.next_token()
	if token.contents == 'title':
		title_nodelist = parser.parse('endtitle')
		token = parser.delete_first_token()
		nodelist = parser.parse('endbox')
    
	parser.delete_first_token()
	return BoxNode(nodelist, title_nodelist, bits[1])

class BoxNode(template.Node):
    def __init__(self, nodelist, title_nodelist, type):
        self.type = template.Variable(type)
        self.nodelist = nodelist
        self.title_nodelist = title_nodelist
        
    def render(self, context):
		output = "<div class=\"box-%s\">" % self.type.resolve(context)
		if self.title_nodelist:
		    output += "<h2>%s</h2>" % self.title_nodelist.render(context)
		output += "<div class=\"content\">"
		output += "<div class=\"content-inner\">"
		output += self.nodelist.render(context)
		output += "</div>"
		output += "</div>"
		output += "</div>"
		return output;
		

class HighlightNode(template.Node):
    def __init__(self, vars, nodelist):
        self.highlights = map(lambda x:template.Variable(x), vars)
        self.nodelist = nodelist        
    
    def render(self, context):
    	result = None
    	try:
        	highlights = filter(None, map(lambda x: x.resolve(context).strip(), self.highlights))
        	if (highlights):
	        	expression = re.compile(r'\b(' + u'|'.join(highlights) + r')\b', re.IGNORECASE|re.UNICODE)  
	        	result = expression.sub(lambda match: '<strong>' + match.group(1) + '</strong>' ,
									    self.nodelist.render(context))
        			
        except template.VariableDoesNotExist:
            return self.nodelist.render(context)
        
        if result == None:
        	result = self.nodelist.render(context)
        
        return result

@register.tag
def highlight(parser, token):
    bits = token.contents.split()
    
    if len(bits) < 1:
        raise template.TemplateSyntaxError("'%s' tag takes atleast one arguments" % bits[0])
    
    nodelist = parser.parse('endhighlight')
    parser.delete_first_token()
    return HighlightNode(bits[1:], nodelist)

@register.filter
@stringfilter
def truncate(value, limit): 
	""" 
 	Truncates strings longer than limit to limit-3 characters, appending an 
 	elipsis. 
 		     
	Argument: Number of characters to truncate to 
	""" 
	try: 
		limit = int(limit) 
	except ValueError: # invalid literal for int() 
		return value # Fail silently. 
	return _truncate(value, limit) 

def _truncate(s, limit): 
	""" 
	Truncates strings longer than limit to limit-3 characters, appending an 
	elipsis. At least one character will always be displayed, so the functional 
	minimum limit is 4. 
	""" 
	s = force_unicode(s) 
	if len(s) <= limit: 
		return s 
	return '%s...' % s[:max(1, limit - 3)] 
	truncate = allow_lazy(truncate, unicode) 