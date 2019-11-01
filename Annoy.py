import database_classes as db
import annoy

t = annoy.AnnoyIndex(7, 'euclidean')

def create_index():
    # area
    area_avg = db.session.query(db.func.avg(db.Mesh.area2D)).scalar()
    area_stddev = db.session.query(db.func.stddev(db.Mesh.area2D)).scalar()
    # perimeter
    perimeter_avg = db.session.query(db.func.avg(db.Mesh.perimeter2D)).scalar()
    perimeter_stddev = db.session.query(db.func.stddev(db.Mesh.perimeter2D)).scalar()
    # rectangularity
    rectangularity_avg = db.session.query(db.func.avg(db.Mesh.rectangularity2D)).scalar()
    rectangularity_stddev = db.session.query(db.func.stddev(db.Mesh.rectangularity2D)).scalar()
    # compactness
    compactness_avg = db.session.query(db.func.avg(db.Mesh.compactness2D)).scalar()
    compactness_stddev = db.session.query(db.func.stddev(db.Mesh.compactness2D)).scalar()
    # diameter
    diameter_avg = db.session.query(db.func.avg(db.Mesh.diameter2D)).scalar()
    diameter_stddev = db.session.query(db.func.stddev(db.Mesh.diameter2D)).scalar()
    # eccentricity
    eccentricity_avg = db.session.query(db.func.avg(db.Mesh.eccentricity2D)).scalar()
    eccentricity_stddev = db.session.query(db.func.stddev(db.Mesh.eccentricity2D)).scalar()
    # skeletonToPerimeterRatio
    skeletonToPerimeterRatio_avg = db.session.query(db.func.avg(db.Mesh.skeletonToPerimeterRatio2D)).scalar()
    skeletonToPerimeterRatio_stddev = db.session.query(db.func.stddev(db.Mesh.skeletonToPerimeterRatio2D)).scalar()
    # bbox_area
    bbox_area_avg = db.session.query(db.func.avg(db.Mesh.bbox_area)).scalar()
    bbox_area_stddev = db.session.query(db.func.stddev(db.Mesh.bbox_area)).scalar()



    armadillo_id = db.session.query(db.Meshtype).filter(db.Meshtype.type=='Armadillo').first()
    meshes = db.session.query(db.Mesh)\
                       .add_columns(db.Mesh.mesh_id,
                                    db.Mesh.area2D,
                                    db.Mesh.perimeter2D,
                                    db.Mesh.diameter2D,
                                    db.Mesh.eccentricity2D,
                                    db.Mesh.compactness2D,
                                    db.Mesh.rectangularity2D,
                                    db.Mesh.skeletonToPerimeterRatio2D,
                                    db.Mesh.bbox_area)\
                       .filter(db.Mesh.meshtype_id!=armadillo_id.meshtype_id)\
                       .all()


    t = annoy.AnnoyIndex(7, 'euclidean')
    for i, mesh in enumerate(meshes, 1):
        v = [(mesh.area2D - area_avg) / area_stddev,
             (mesh.perimeter2D - perimeter_avg) / perimeter_stddev,
             (mesh.rectangularity2D - rectangularity_avg) / rectangularity_stddev,
             (mesh.diameter2D - diameter_avg) / diameter_stddev,
             (mesh.skeletonToPerimeterRatio2D - skeletonToPerimeterRatio_avg) / skeletonToPerimeterRatio_stddev,
             (mesh.eccentricity2D - eccentricity_avg) / eccentricity_stddev,
             (mesh.compactness2D - compactness_avg) / compactness_stddev]
        t.add_item(mesh.mesh_id, v)

    t.build(100)
    t.save('infomr.ann')
    return t

def load_index():
    t = annoy.AnnoyIndex(7, 'euclidean')
    t.load('infomr.ann')
    return t

def main():

    mesh_filename = 'Cup/22.off'
    mesh_index = db.session.query(db.Mesh.mesh_id).filter(db.Mesh.filename == mesh_filename).first()
    t = create_index()
    nns = t.get_nns_by_item(mesh_index.mesh_id, 20)

    # nns_filenames = []
    print('Meshes similar to: {}'.format(mesh_filename))
    for index in nns:
        q_nns = db.session.query(db.Mesh.filename).filter(db.Mesh.mesh_id == index).first()
        # nns_filenames.append(q_nns.filename)
        print(q_nns.filename)



if __name__ == '__main__':
    main()

