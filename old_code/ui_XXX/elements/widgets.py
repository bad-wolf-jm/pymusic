
from kivy.lang import Builder


kv_string = """
<HDivider@Widget>
    size_hint: 1, None
    height: 1
    canvas.after:
        Color:
            rgba: 1, 1, 1, .8
        Line:
            points: [self.pos[0],self.pos[1], self.pos[0] + self.width, self.pos[1]]
        Rectangle:
            pos:self.pos
            size: self.size

<VDivider@Widget>
    size_hint: None, 1
    width: 1
    canvas.after:
        Color:
            rgba: 1, 1, 1, .8
        Line:
            points: [self.pos[0], self.pos[1], self.pos[0], self.pos[1]+self.height]
        Rectangle:
            pos:self.pos
            size: self.size

<ModalHDivider@Widget>
    size_hint: 1, None
    height: 1
    canvas.after:
        Color:
            rgba: .2, .2, .2, .8
        Line:
            points: [self.pos[0],self.pos[1], self.pos[0] + self.width, self.pos[1]]
        Rectangle:
            pos:self.pos
            size: self.size

<ModalVDivider@Widget>
    size_hint: None, 1
    width: 1
    canvas.after:
        Color:
            rgba: .2,.2,.2, .8
        Line:
            points: [self.pos[0], self.pos[1], self.pos[0], self.pos[1]+self.height]
        Rectangle:
            pos:self.pos
            size: self.size




<OneLineLabel@Label>:
    text_size: self.size
    size_hint: 1, 1
    shorten: True
    markup: True
    ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
    halign: 'left'
    valign: 'middle'
    font_size: 15
    #text_size: self.size

<ListItemLabel@OneLineLabel>:
    text_size: self.size
    size_hint: 1, 1
    shorten: True
    markup: True
    ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
    halign: 'left'
    valign: 'middle'
    font_size: 15

<VerticalBox@BoxLayout>:
    orientation: 'vertical'
    size_hint: 1,1
    padding: [5,5,5,5]
    spacing: 5

<HorizontalBox@BoxLayout>:
    orientation: 'horizontal'
    size_hint: 1,1
    padding: [5,5,5,5]
    spacing: 5

<ColoredRectangle@RelativeLayout>:
    size_hint: 1,1
    rect_color: 0,0,0,1
    canvas.before:
        Color:
            rgba: self.rect_color
        Rectangle:
            size: self.size
            pos:  self.pos



"""

Builder.load_string(kv_string)
