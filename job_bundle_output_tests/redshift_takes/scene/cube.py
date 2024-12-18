import os

import c4d


def main():
    doc = c4d.documents.GetActiveDocument()
    doc.Flush()
    cube = c4d.BaseObject(c4d.Ocube)
    cube[c4d.PRIM_CUBE_LEN] = c4d.Vector(200, 200, 200)
    cube.SetAbsPos(c4d.Vector(0, 170, -170))
    doc.InsertObject(cube)
    take_data = doc.GetTakeData()
    main_take = take_data.GetMainTake()
    take_a = take_data.AddTake("", main_take, main_take)
    take_a.SetName("A")
    take_data.SetCurrentTake(take_a)
    take_a.OverrideNode(take_data, cube, False)
    cube[c4d.PRIM_CUBE_LEN] = c4d.Vector(100, 100, 100)
    take_data.SetCurrentTake(main_take)
    render_data = doc.GetActiveRenderData()
    render_data[c4d.RDATA_PATH] = "renders/$prj_$take"
    frame_start = c4d.BaseTime(1, doc.GetFps())
    frame_end = c4d.BaseTime(1, doc.GetFps())
    render_data[c4d.RDATA_FRAMEFROM] = frame_start
    render_data[c4d.RDATA_FRAMETO] = frame_end
    render_data[c4d.RDATA_RENDERENGINE] = 1036219  # redshift
    save_dir = os.path.dirname(__file__)
    save_name = "redshift_takes.c4d"
    save_file = os.path.join(save_dir, save_name)
    doc.SetDocumentPath(save_dir)
    doc.SetDocumentName(save_name)
    c4d.documents.SaveDocument(doc, save_file, c4d.SAVEDOCUMENTFLAGS_0, c4d.FORMAT_C4DEXPORT)
    c4d.documents.InsertBaseDocument(doc)
    c4d.EventAdd()


if __name__ == "__main__":
    main()
