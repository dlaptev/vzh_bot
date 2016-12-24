# -*- coding: utf-8 -*-

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from urlparse import urlparse
import StringIO
import json
import urllib
import webapp2

RATIO = 1.85  # Average height/width ratio of a letter in Impact.ttf.
SEPARATOR = '~!~!~'  # Unique string separator.
# Text box size and offsets.
TEXT_H = 80
TEXT_W = 263
SHIFT_Y = 200
SHIFT_X = 215

def split_into_lines(text, no_lines):
  if no_lines == 1:
    return text
  shift = int(len(text) / no_lines)
  space_pos = shift
  for i in range(shift):
    if text[shift + i] == ' ':
      space_pos = shift + i
    elif text[shift - i] == ' ':
      space_pos = shift - i
    if text[space_pos] == ' ':
      return text[:space_pos] + SEPARATOR + \
             split_into_lines(text[space_pos + 1:], no_lines - 1)
  return 'error'  # Should never happen when called from vzhuh_formatter.

def vzhuh_formatter(text):
  text = ' '.join(text.split())  # Remove double and trailing spaces.
  best_res = { 'area': 0.0 }
  for no_lines in range(1, len(text.split()) + 1):
    lines = split_into_lines(text, no_lines).split(SEPARATOR)
    max_line_len = max(map(lambda x: len(x), lines))
    min_font_size = min(int(TEXT_W * RATIO / max_line_len),
                        int(TEXT_H / no_lines))
    for s in range(11):
      (area, height, font_sizes) = (0.0, 0.0, [])
      for line in lines:
        font_size = int(min_font_size * s / 10.0 +
                        TEXT_W * RATIO / len(line) * (1.0 - s / 10.0))
        font_sizes.append(font_size)
        height += font_size
        area += len(line) * font_size * font_size / RATIO
      if height <= TEXT_H:
        if area > best_res['area']:
          best_res = { 'area': area, 'lines': lines, 'font_sizes': font_sizes }
  return best_res

class VzhuhImage(webapp2.RequestHandler):
  def get(self):
    text = self.request.get('t')
    if len(text) > 200 or len(text.split()) > 20:
      text = u'и бот сломался!'
    res = vzhuh_formatter((u'ВЖУХ, ' + text).upper())
    img = Image.open('vzhuh.jpeg')
    draw = ImageDraw.Draw(img)
    shift = SHIFT_Y
    for i in range(len(res['lines'])):
      font = ImageFont.truetype('Impact.ttf', size=res['font_sizes'][i])
      draw.text((SHIFT_X, shift), res['lines'][i], (0,0,0), font=font)
      shift += res['font_sizes'][i]
    # Convert a PIL image to a suitable return format.
    output = StringIO.StringIO()
    img.save(output, format="jpeg")
    text_layer = output.getvalue()
    output.close()
    self.response.headers['Content-Type'] = 'image/jpeg'
    self.response.write(text_layer)

class VzhuhWebHook(webapp2.RequestHandler):
  def post(self):
    requ = json.loads(self.request.body)
    print requ
    if not('message' in requ and 'text' in requ['message']):
      # TODO: something strange - just ignore for now.
      return
    text = requ['message']['text']
    if text[0] == '/':  # Parse commands.
      if text[:4] == '/vz ' and len(text) > 4:  # /vz with text.
        text = text[4:]
      elif text[:3] == '/vz':  # /vz without text.
        self.response.headers['Content-Type'] = 'application/json'
        resp = { 'method': 'sendMessage',
                 'chat_id': requ['message']['chat']['id'],
                 'text': u'нужно ввести текст, например \"/vz и готово\"' }
        self.response.write(json.dumps(resp))
        return
      else:  # Unrecognized command - just ignore for now.
        return
    # Send the message with the photo link.
    self.response.headers['Content-Type'] = 'application/json'
    img_url = 'http://%s/vzhuh/img?t=%s' % (urlparse(self.request.url).netloc,
        urllib.quote_plus(text.encode('utf8')))
    resp = { 'method': 'sendPhoto',
             'chat_id': requ['message']['chat']['id'],
             'photo': img_url }
    self.response.write(json.dumps(resp))


app = webapp2.WSGIApplication([
  ('/vzhuh/img.*', VzhuhImage),
  ('/vzhuh/webhook.*', VzhuhWebHook),
], debug=True)
