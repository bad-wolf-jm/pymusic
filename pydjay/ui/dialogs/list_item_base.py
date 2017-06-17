from pydjay.ui.elements import list_item_base


class ModalListItemBase(list_item_base.ListItemBase):
    def __init__(self, row=None, item=None, view=None, drag_context=None, *args, **kwargs):
        super(ModalListItemBase, self).__init__(*args, **kwargs)
        self.even_color = [0.7, 0.7, 0.7, 0.8]
        self.odd_color = [0.6, 0.6, 0.6, 0.8]
        self.selected_text_color = [0.6, 0.6, 0.6, 0.8]
        self.selected_color_focus = [.5, .5, .5, 1]
        self.selected_color_no_focus = [.5, .5, .5, .7]
