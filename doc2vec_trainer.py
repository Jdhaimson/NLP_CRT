import argparse
import lockfile

from daemon import DaemonContext
from gensim.models import Doc2Vec
from gensim.models.doc2vec import LabeledSentence

from loader import get_data


class LabeledDocIterator(object):
    def __init__(self, patient_list, categories, status):
        self.patient_list = patient_list 
        self.category = categories
        self.status = status

    def __iter__(self):
        for i in self.patient_list:
            p = get_data([i])[0]
            self.status.write(p['NEW_EMPI'] + '\n')
            for category in categories:
                if category in p:
                    for idx, doc in enumerate(p[category]):
                        tag = p['NEW_EMPI'] + '_' + category + '_' + str(idx) + '\n'
                        yield LabeledSentence(words=doc['free_text'].split(), tags=[tag])


def train_doc2vec_model(categories, n_patients, output_file, status_file, dm):
    with open(status_file, 'w') as status:
        it = LabeledDocIterator(range(n_patients), categories, status)

        model = Doc2Vec(size=300, window=10, dm=dm, min_count=5, workers=11,alpha=0.025, min_alpha=0.025) # use fixed learning rate
        model.build_vocab(it)
        for epoch in range(10):
            message = ("***********Training Epoch: " + str(epoch)
                       + ("***********") + '\n')
            print(message)
            status.write(message)
            model.train(it)
            model.alpha -= 0.002 # decrease the learning rate
            model.min_alpha = model.alpha # fix the learning rate, no decay
            model.train(it)

        # Save the model
        model.save(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output_file")
    parser.add_argument("n_patients")
    parser.add_argument("categories")
    # Switches between Distributed Memory and Distributed Bag of Words Model
    parser.add_argument("dm")
    args = parser.parse_args()
    status_file = args.output_file + '.status'
    categories = args.categories.split(',')


    base = '/home/ubuntu/josh_project'
    context = DaemonContext(
        working_directory=base,
        umask=0o002,
        pidfile=lockfile.FileLock(base + 'doc2vec_trainer.pid'),
    )

    with context:
        train_doc2vec_model(categories, int(args.n_patients), 
                        args.output_file, status_file, int(args.dm))
