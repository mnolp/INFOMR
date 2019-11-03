import meshTools
import Mesh
import os
import Mesh2D
import database_classes as db
from sqlalchemy import func
import time
from scipy.spatial import distance
from scipy.stats import wasserstein_distance


def getofffiles(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.off') and not file.endswith('_processed.off'):
                files.append(os.path.join(r, file))

    return files

def getpngfiles(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith('.png'):
                files.append(os.path.join(r, file))

    return files


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



def old_main():
    files = getofffiles("Armadillo/")
    # files = ["dataset/Ant/95.off"]
    #
    for n, filepath in enumerate(files, 1):
        start_time = time.time()

        print ("Number {} out of {}, file: {}".format(n, len(files), filepath))
        # with open(filepath, "r") as f:
        #     shape, vertexes, faces = meshTools.read_off(f)
        # m = Mesh.Mesh(filepath, vertexes, faces)
        # m.setMeshToCenter()
        # m.eigen()
        # m.changingBase()
        # m.setBoundingBox()
        # m.normalizeMesh()
        # m.flipTest()
        # processed_file = m.toFile()
        # filepath2D = m.toimage()
        # update_mesh(filepath, m)

        # meshTools.meshRenderer(processed_file, m.eigenvectors)
        distances, meshes = matching_std(filepath)
        for i in range(len(distances)):
            id1 = db.session.query(db.Mesh.mesh_id).filter(db.Mesh.filename==filepath[filepath.find('/')+1:]).first()
            id2 = db.session.query(db.Mesh.mesh_id).filter(db.Mesh.filename==meshes[i]).first()
            if not id1 == id2:
                db.session.add(db.Distance(
                    mesh1_id=id1,
                    mesh2_id=id2,
                    value=distances[i]
                ))
        db.session.commit()

        print("Elapsed time: {}".format(time.time()-start_time))


    # m2D2 = Mesh2D.Mesh2D("dataset/Airplane/80_silhouette.png")
    #
    # print(m2D1.area)
    # print(m2D2.area)


from Annoy import load_index
def evaluate_out_of_20():
    t = load_index('no_arm.ann')
    files = getofffiles('dataset')

    classes = db.session.query(db.Meshtype.type).filter(~db.Meshtype.type.in_(['Armadillo',
                                                        'Bust',
                                                        'Vase',
                                                        'Mech',
                                                        'Bearing'])).all()
    true_positives = {c.type: 0 for c in classes}
    true_negatives = {c.type: 0 for c in classes}
    false_positives = {c.type: 0 for c in classes}
    false_negatives = {c.type: 0 for c in classes}

    for i, filename in enumerate(files):
        mesh = db.session.query(db.Mesh).filter(db.Mesh.filename == filename[filename.index('/')+1: ]).first()
        mesh_class = db.session.query(db.Meshtype).filter(db.Meshtype.meshtype_id==mesh.meshtype_id).first()

        similar_meshes_id = t.get_nns_by_item(mesh.mesh_id, 20)
        # similar_meshes_id = [x if x < 340 else x+20 for x in similar_meshes_id]
        # similar_meshes_id = db.session.query(db.Distance).filter(db.Distance.mesh1_id==mesh.mesh_id).order_by(db.Distance.value).all()

        # similar_meshes = [db.session.query(db.Mesh).filter(db.Mesh.mesh_id==x.mesh2_id).first() for x in similar_meshes_id]
        # similar_meshes = similar_meshes[:20]

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

    for key in precision:
        try:
            precision[key] = true_positives[key]/(true_positives[key]+false_positives[key])
            recall[key] = true_positives[key]/(true_positives[key]+false_negatives[key])
            print("Class: {}, Precision: {}, Recall: {}".format(key, precision[key], recall[key]))
        except(ZeroDivisionError):
            print("Error on class: {}".format(key))

def evaluate_get_all():
    t = load_index('no_arm.ann')
    files = getofffiles('dataset')

    classes = db.session.query(db.Meshtype.type).filter(~db.Meshtype.type.in_(['Armadillo',
                                                        'Bust',
                                                        'Vase',
                                                        'Mech',
                                                        'Bearing'])).all()
    true_positives = {c.type: 0 for c in classes}
    true_negatives = {c.type: 0 for c in classes}
    false_positives = {c.type: 0 for c in classes}
    false_negatives = {c.type: 0 for c in classes}

    for i, filename in enumerate(files):
        mesh = db.session.query(db.Mesh).filter(db.Mesh.filename == filename[filename.index('/')+1: ]).first()
        mesh_class = db.session.query(db.Meshtype).filter(db.Meshtype.meshtype_id==mesh.meshtype_id).first()

        similar_meshes_id = t.get_nns_by_item(mesh.mesh_id, 280)
        # similar_meshes_id = [x if x < 340 else x+20 for x in similar_meshes_id]
        # similar_meshes_id = db.session.query(db.Distance).filter(db.Distance.mesh1_id==mesh.mesh_id).order_by(db.Distance.value).all()

        # similar_meshes = [db.session.query(db.Mesh).filter(db.Mesh.mesh_id==x.mesh2_id).first() for x in similar_meshes_id]
        # similar_meshes = similar_meshes[:20]

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

    for key in precision:
        try:
            precision[key] = true_positives[key]/(true_positives[key]+false_positives[key])
            recall[key] = true_positives[key]/(true_positives[key]+false_negatives[key])
            print("Class: {}, Precision: {}, Recall: {}".format(key, precision[key], recall[key]))
        except(ZeroDivisionError):
            print("Error on class: {}".format(key))

def main():
    evaluate_get_all()
if __name__ == "__main__":
    main()