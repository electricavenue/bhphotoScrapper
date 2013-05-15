import re
price='<span class="value act_forDetails">$1,499.00</span>'

print re.search('"*.value.*"',price).group().replace("\"",'')