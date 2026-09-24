# -*- coding: utf-8 -*-
import os, sys
import win32com.client

def export():
    in_file = os.path.abspath('Docs/Thesis_OBE/Thesis_Poster.pptx')
    pdf_file = os.path.abspath('Docs/Thesis_OBE/Thesis_Poster.pdf')
    png_file = os.path.abspath('Docs/Thesis_OBE/Thesis_Poster.png')

    print(f'Opening: {in_file}')
    ppt_app = win32com.client.DispatchEx('PowerPoint.Application')
    try:
        presentation = ppt_app.Presentations.Open(in_file, WithWindow=False)
        print('Exporting PDF...')
        presentation.SaveAs(pdf_file, 32)  # ppSaveAsPDF = 32
        print(f'PDF saved: {pdf_file}')

        print('Exporting high-res PNG...')
        slide = presentation.Slides(1)
        slide.Export(png_file, 'PNG', 3600, 4800)
        print(f'PNG saved: {png_file}')

        presentation.Close()
    finally:
        ppt_app.Quit()

if __name__ == '__main__':
    export()
