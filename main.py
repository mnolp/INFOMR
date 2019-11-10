import meshTools
import Mesh
import os
import Mesh2D
import database_classes as db
from sqlalchemy import func
import time
from scipy.spatial import distance


'''
Function to find all off files in path and return them as a list
'''
def getofffiles(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.off') and not file.endswith('_processed.off'):
                files.append(os.path.join(r, file))

    return files

'''
Function to find all png files in path and return them as a list
'''
def getpngfiles(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.png'):
                files.append(os.path.join(r, file))

    return files

'''
Function to add a mesh (m, m2D) with filepath to the database
'''
def add_mesh(filepath, m, m2D):
    db.session.add(db.Mesh(
        filename=filepath,
        meshtype_id=db.session.query(db.Meshtype.meshtype_id).filter(
            db.Meshtype.type == filepath[
                                  filepath[:filepath.rfind('/')].rfind('/') + 1: filepath.rfind('/')]).first()[
            0],
        area2D=m2D.area,
        compactness2D=m2D.compactness,
        rectangularity2D=m2D.rectangularity,
        diameter2D=m2D.diameter,
        eccentricity2D=m.eigenvalues[0] / m.eigenvalues[1],
        perimeter2D=m2D.perimeter,
        skeletonToPerimeterRatio2D=m2D.skeleton_length / m2D.perimeter,
        bbox_area=abs(m2D.bounding_box[0]*m2D.bounding_box[1])
    ))
    db.session.commit()

'''
Function to update an already existing mesh with new values
'''
def update_mesh(filepath, m):
    m2D = Mesh2D.Mesh2D(
        'dataset/'+filepath[: filepath.rfind('/')] + filepath[filepath.rfind('/'): filepath.rfind('.')] + "_silhouette.png")

    q = db.session.query(db.Mesh).filter(db.Mesh.filename == filepath).first()
    q.area2D = m2D.area
    q.compactness2D = m2D.compactness
    q.rectangularity2D = m2D.rectangularity
    q.diameter2D = m2D.diameter
    q.eccentricity2D = m.eigenvalues[0] / m.eigenvalues[1]
    q.perimeter2D = m2D.perimeter
    q.skeletonToPerimeterRatio2D = m2D.skeleton_length / m2D.perimeter
    q.bbox_area = float(m2D.bounding_box[0] * m2D.bounding_box[1])

    db.session.commit()

'''
Function that return the first 20 similar meshes querying the database
'''
def matching_std(filepath):
    # area
    area_avg = db.session.query(func.avg(db.Mesh.area2D)).scalar()
    area_stddev = db.session.query(func.stddev(db.Mesh.area2D)).scalar()
    # perimeter
    perimeter_avg = db.session.query(func.avg(db.Mesh.perimeter2D)).scalar()
    perimeter_stddev = db.session.query(func.stddev(db.Mesh.perimeter2D)).scalar()
    # rectangularity
    rectangularity_avg = db.session.query(func.avg(db.Mesh.rectangularity2D)).scalar()
    rectangularity_stddev = db.session.query(func.stddev(db.Mesh.rectangularity2D)).scalar()
    # compactness
    compactness_avg = db.session.query(func.avg(db.Mesh.compactness2D)).scalar()
    compactness_stddev = db.session.query(func.stddev(db.Mesh.compactness2D)).scalar()
    # diameter
    diameter_avg = db.session.query(func.avg(db.Mesh.diameter2D)).scalar()
    diameter_stddev = db.session.query(func.stddev(db.Mesh.diameter2D)).scalar()
    # eccentricity
    eccentricity_avg = db.session.query(func.avg(db.Mesh.eccentricity2D)).scalar()
    eccentricity_stddev = db.session.query(func.stddev(db.Mesh.eccentricity2D)).scalar()
    # skeletonToPerimeterRatio
    skeletonToPerimeterRatio_avg = db.session.query(func.avg(db.Mesh.skeletonToPerimeterRatio2D)).scalar()
    skeletonToPerimeterRatio_stddev = db.session.query(func.stddev(db.Mesh.skeletonToPerimeterRatio2D)).scalar()
    # bbox_area
    bbox_area_avg = db.session.query(func.avg(db.Mesh.bbox_area)).scalar()
    bbox_area_stddev = db.session.query(func.stddev(db.Mesh.bbox_area)).scalar()

    m2D = db.session.query(db.Mesh).filter(db.Mesh.filename==filepath[filepath.find('/')+1:]).first()

    meshes = db.session.query(db.Mesh).all()

    distances = []
    files = []
    for i, mesh in enumerate(meshes):

        u = [(mesh.area2D-area_avg)/area_stddev,
             (mesh.perimeter2D-perimeter_avg)/perimeter_stddev,
             (mesh.rectangularity2D-rectangularity_avg)/rectangularity_stddev,
             (mesh.diameter2D-diameter_avg)/diameter_stddev,
             (mesh.skeletonToPerimeterRatio2D-skeletonToPerimeterRatio_avg)/skeletonToPerimeterRatio_stddev,
             (mesh.eccentricity2D-eccentricity_avg)/eccentricity_stddev,
             (mesh.compactness2D-compactness_avg)/compactness_stddev]

        v = [(m2D.area2D-area_avg)/area_stddev,
             (m2D.perimeter2D-perimeter_avg)/perimeter_stddev,
             (m2D.rectangularity2D-rectangularity_avg)/rectangularity_stddev,
             (m2D.diameter2D-diameter_avg)/diameter_stddev,
             (m2D.skeletonToPerimeterRatio2D-skeletonToPerimeterRatio_avg)/skeletonToPerimeterRatio_stddev,
             (m2D.eccentricity2D-eccentricity_avg)/eccentricity_stddev,
             (m2D.compactness2D-compactness_avg)/compactness_stddev]

        distances.append(distance.euclidean(u, v))
        files.append(mesh.filename)

    for i in range(20):
        max_dist = distances.index(min(distances))
        print ("File: {}, Distance: {}".format(files[max_dist], distances[max_dist]))

        del distances[max_dist]
        del files[max_dist]
    return (distances, files)


'''
Function that noramlise a mesh and save its silhouette
'''
def extract_silhouette(files):
    for n, filepath in enumerate(files, 1):
        start_time = time.time()

        print ("Number {} out of {}, file: {}".format(n, len(files), filepath))
        with open(filepath, "r") as f:
            shape, vertexes, faces = meshTools.read_off(f)
        m = Mesh.Mesh(filepath, vertexes, faces)
        m.setMeshToCenter()
        m.eigen()
        m.changingBase()
        m.setBoundingBox()
        m.normalizeMesh()
        m.flipTest()
        processed_file = m.toFile()
        filepath2D = m.toimage()
        
        print("Elapsed time: {}".format(time.time()-start_time))


'''
Function that evaluates the system set with ANN index, store the result in csv file
'''
from Annoy import load_index, create_index
def evaluate_out_of_20():
    banned_classes_ids = [3, 6, 11, 18, 20]
    t = create_index(banned_classes_ids)
    banned_classes = db.session.query(db.Meshtype.type).filter(db.Meshtype.meshtype_id.in_(banned_classes_ids)).all()
    banned_classes = [x.type for x in banned_classes]
    files = getofffiles('dataset')
    classes = db.session.query(db.Meshtype.type).filter(~db.Meshtype.meshtype_id.in_(banned_classes_ids)).all()
    true_positives = {c.type: 0 for c in classes}
    true_negatives = {c.type: 0 for c in classes}
    false_positives = {c.type: 0 for c in classes}
    false_negatives = {c.type: 0 for c in classes}

    for i, filename in enumerate(files):
        if filename.split('/')[1] not in banned_classes:
            mesh = db.session.query(db.Mesh).filter(db.Mesh.filename == filename[filename.index('/')+1: ]).first()
            mesh_class = db.session.query(db.Meshtype).filter(db.Meshtype.meshtype_id==mesh.meshtype_id).first()

            similar_meshes_id, similar_meshes_distances = t.get_nns_by_item(mesh.mesh_id, 20, include_distances=True)

            similar_meshes = [db.session.query(db.Mesh).filter(db.Mesh.mesh_id==id).first() for id in similar_meshes_id]
            true_pos = 0
            for sm in similar_meshes:
                mc = db.session.query(db.Meshtype).filter(db.Meshtype.meshtype_id==sm.meshtype_id).first()
                true_pos += 1 if mesh_class==mc else 0

        true_positives[mesh_class.type] += true_pos
        false_positives[mesh_class.type] += 20-true_pos
        false_negatives[mesh_class.type] += 20-true_pos
        true_negatives[mesh_class.type] += len(files)-false_negatives[mesh_class.type]

    precision = {c.type: 0 for c in classes}
    recall = {c.type: 0 for c in classes}

    with open("prec_rec.csv", "w") as outf:
        outf.write("Class;Precision;Recall;\n")
        for key in precision:
            try:
                precision[key] = true_positives[key]/(true_positives[key]+false_positives[key])
                recall[key] = true_positives[key]/(true_positives[key]+false_negatives[key])
                outf.write("{};{};{};\n".format(key, precision[key], recall[key]).format(key, precision[key], recall[key]))
                print("Class: {}; Precision: {}; Recall: {}".format(key, precision[key], recall[key]))
            except(ZeroDivisionError):
                print("Error on class: {}".format(key))

'''
Function that evaluates the system set to work with a recall equals to 1, sotres the results in a csv file
'''
def evaluate_get_all():
    banned_classes_ids = []
    t = create_index(banned_classes_ids)
    banned_classes = db.session.query(db.Meshtype.type).filter(db.Meshtype.meshtype_id.in_(banned_classes_ids)).all()
    banned_classes = [x.type for x in banned_classes]
    files = getofffiles('dataset')


    classes = db.session.query(db.Meshtype.type).filter(~db.Meshtype.type.in_(banned_classes)).all()
    true_positives = {c.type: 0 for c in classes}
    true_negatives = {c.type: 0 for c in classes}
    false_positives = {c.type: 0 for c in classes}
    false_negatives = {c.type: 0 for c in classes}

    for i, filename in enumerate(files):
        if filename.split('/')[1] not in banned_classes:
            print(filename)
            mesh = db.session.query(db.Mesh).filter(db.Mesh.filename == filename[filename.index('/')+1: ]).first()
            mesh_class = db.session.query(db.Meshtype).filter(db.Meshtype.meshtype_id==mesh.meshtype_id).first()

            similar_meshes_id = t.get_nns_by_item(mesh.mesh_id, 280)

            similar_meshes = [db.session.query(db.Mesh).filter(db.Mesh.mesh_id==id).first() for id in similar_meshes_id]
            true_pos = 0
            for num, sm in enumerate(similar_meshes):
                mc = db.session.query(db.Meshtype).filter(db.Meshtype.meshtype_id==sm.meshtype_id).first()
                true_pos += 1 if mesh_class==mc else 0
                if true_pos==20: break

        true_positives[mesh_class.type] += true_pos
        false_positives[mesh_class.type] += num-true_pos
        # false_negatives[mesh_class.type] += 20-true_pos
        true_negatives[mesh_class.type] += len(files)-num

    precision = {c.type: 0 for c in classes}
    recall = {c.type: 0 for c in classes}

    with open("prec_rec.csv", "w") as outf:
        outf.write("Class,Precision,Recall,\n")
    for key in precision:
        try:
            precision[key] = true_positives[key]/(true_positives[key]+false_positives[key])
            recall[key] = true_positives[key]/(true_positives[key]+false_negatives[key])
            outf.write("{},{},{},\n".format(key, precision[key], recall[key]).format(key, precision[key], recall[key]))
            print("Class: {}, Precision: {}, Recall: {}".format(key, precision[key], recall[key]))
        except(ZeroDivisionError):
            print("Error on class: {}".format(key))

def main():
    evaluate_out_of_20()

if __name__ == "__main__":
    main()
