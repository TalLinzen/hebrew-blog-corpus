from xlwt import XFStyle, Alignment

left = XFStyle()
left_alignment = Alignment()
left_alignment.horz = Alignment.HORZ_LEFT
left_alignment.dire = Alignment.DIRECTION_RL
left.alignment = left_alignment

right = XFStyle()
right_alignment = Alignment()
right_alignment.horz = Alignment.HORZ_RIGHT
right_alignment.dire = Alignment.DIRECTION_RL
right.alignment = right_alignment

center = XFStyle()
center_alignment = Alignment()
center_alignment.horz = Alignment.HORZ_CENTER
center_alignment.direction = Alignment.DIRECTION_RL
center.alignment = center_alignment
