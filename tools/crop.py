from PIL import Image
img = Image.open('E:/AI/classmate/docs/shots/e2e_popup_name.png')
w, h = img.size
img.crop((0, 0, w, 420)).save('E:/AI/classmate/docs/shots/_popup_card.png')
img.crop((0, 90, w, 330)).save('E:/AI/classmate/docs/shots/_popup_mid.png')
print('ok', img.size)
