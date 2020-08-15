from skmultiflow.data.random_rbf_generator import RandomRBFGenerator
from skmultiflow.utils import check_random_state
import numpy as np
import random


class RandomRBFGeneratorDrift(RandomRBFGenerator):
    """ Random Radial Basis Function stream generator with concept drift.

    This class is an extension from the RandomRBFGenerator. It functions
    as the parent class, except that drift can be introduced in objects
    of this class.

    The drift is created by adding a speed to certain centroids. As the
    samples are generated each of the moving centroids' centers is
    changed by an amount determined by its speed.

    Parameters
    ----------
    model_random_state: int, RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used by `np.random`..

    sample_random_state: int, RandomState instance or None, optional (default=None)
        If int, random_state is the seed used by the random number generator;
        If RandomState instance, random_state is the random number generator;
        If None, the random number generator is the RandomState instance used by `np.random`..

    n_classes: int (Default: 2)
        The number of class labels to generate.

    n_features: int (Default: 10)
        The number of numerical attributes to generate.

    n_centroids: int (Default: 50)
        The number of centroids to generate.

    change_speed: float (Default: 0.0)
        The concept drift speed.

    num_drift_centroids: int (Default: 50)
        The number of centroids that will drift.

 uncomment below and change random_rbf_generator.py accordingly:
    def __init__(self, model_random_state=None, sample_random_state=None, n_classes=2,n_features=10, n_centroids=50,class_weights=[]):

        if (len(class_weights)!=n_classes):
          class_weights = np.zeros(n_classes) + 1/n_classes
        self.class_weights = class_weights

    def _generate_centroids(self):
            # self.centroids[i].class_label = model_random_state.randint(self.n_classes) # replace with:
            self.centroids[i].class_label = random.choices(range(self.n_classes),weights=self.class_weights,k=1)


    --------
    >>> # Imports
    >>> from skmultiflow.data.random_rbf_generator_drift import RandomRBFGeneratorDrift
    >>> # Setting up the stream
    >>> stream = RandomRBFGeneratorDrift(model_random_state=99, sample_random_state = 50,
    ...  n_classes = 4, n_features = 10, n_centroids = 50, change_speed=0.87,
    ...  num_drift_centroids=50)
    >>> # Retrieving one sample
    >>> stream.next_sample()
    (array([[ 0.87640769,  1.11561069,  0.61592869,  1.0580048 ,  0.34237265,
         0.44265564,  0.8714499 ,  0.47178835,  1.07098717,  0.29090414]]), array([ 3.]))
    >>> # Retrieving 10 samples
    >>> stream.next_sample(10)
    (array([[ 0.78413886,  0.98797944,  0.26981191,  0.92217135,  0.61152321,
         1.02183543,  0.99855968,  0.71545227,  0.55584282,  0.32919095],
       [ 0.45714164,  0.2610933 ,  0.07065982,  0.62751192,  0.75317802,
         0.95785718,  0.32732265,  1.03553576,  0.58009199,  0.90331289],
       [ 0.04165148,  0.38215897, -0.0173352 ,  0.64773072,  0.50398859,
         1.00646399, -0.03972425,  0.62976581,  0.70082235,  0.90992945],
       [ 0.37416657,  0.45838559,  0.82463152,  0.17117448,  0.97320165,
         0.73638815,  0.80587782,  0.75280346,  0.40483112,  1.0012537 ],
       [ 0.79264171,  0.13507299,  0.79600514,  0.33743781,  0.67766074,
         0.70102531, -0.02483112,  0.1921961 ,  0.46693386, -0.02937016],
       [ 0.5129367 ,  0.42697567,  0.25741495,  0.68854096,  0.1119384 ,
         0.76748539,  0.91141342,  0.51498633,  0.17019881,  0.51172656],
       [-0.07820356,  1.19744888,  0.82647513,  1.08993095,  0.67718824,
         0.66486463,  0.52000702,  0.68708254,  0.21171053,  0.81696899],
       [ 0.57232341,  1.13725733,  0.97343092,  1.11889521,  0.68894022,
         1.27717546, -0.1063654 , -0.36732086,  0.54799583,  0.48858978],
       [ 0.27969972, -0.06563579,  0.02834469,  0.05250523,  0.52713213,
         0.73472713,  0.15381198, -0.07735765,  0.9792027 ,  0.92673772],
       [ 0.52641196,  0.3009952 ,  0.56104759,  0.40478501,  0.63097374,
         0.3797032 , -0.00446842,  0.52913688,  0.24908855,  0.22779074]]),
        array([ 3.,  3.,  3.,  2.,  3.,  2.,  0.,  2.,  0.,  2.]))
    >>> # Generators will have infinite remaining instances, so it returns -1
    >>> stream.n_remaining_samples()
    -1
    >>> stream.has_more_samples()
    True

    """

    def __init__(self, model_random_state=None, sample_random_state=None, n_classes=2,
                 n_features=10, n_centroids=50, change_speed=0.0, num_drift_centroids=50, class_weights=[]):
        # Default values
        self.change_speed = change_speed
        self.num_drift_centroids = num_drift_centroids
        self.centroid_speed = None
        if len(class_weights) != n_classes:
            class_weights = np.zeros(n_classes) + 1 / n_classes
        self.class_weights = class_weights

        super().__init__(model_random_state=model_random_state,
                         sample_random_state=sample_random_state,
                         n_classes=n_classes,
                         n_features=n_features, n_centroids=n_centroids)

        self.name = "Random RBF Generator with drift"

    def next_sample(self, batch_size=1):
        """ Returns next sample from the stream.

        Return batch_size samples generated by choosing a centroid at
        random and randomly offsetting its attributes so that it is
        placed inside the hypersphere of that centroid.

        In addition to that, drift is introduced to a chosen number of
        centroids. Each chosen center is moved at each generated sample.

        Parameters
        ----------
        batch_size: int (optional, default=1)
            The number of samples to return.

        Returns
        -------
        tuple or tuple list
            Return a tuple with the features matrix and the labels matrix for
            the batch_size samples that were requested.

        """
        data = np.zeros([batch_size, self.n_num_features + 1])
        for k in range(batch_size):
            num_drift_centroids = self.num_drift_centroids
            if num_drift_centroids > self.n_centroids:
                num_drift_centroids = self.n_centroids

            for i in range(num_drift_centroids):
                for j in range(self.n_num_features):
                    self.centroids[i].centre[j] += self.centroid_speed[i][j] * self.change_speed

                    if (self.centroids[i].centre[j] > 1) or (self.centroids[i].centre[j] < 0):
                        self.centroids[i].centre[j] = 1 if (self.centroids[i].centre[j] > 1) else 0
                        self.centroid_speed[i][j] = -self.centroid_speed[i][j]
            X, y = super().next_sample(1)
            data[k, :] = np.append(X, y)

        self.current_sample_x = data[:, :self.n_num_features]
        self.current_sample_y = data[:, self.n_num_features:].flatten().astype(int)
        return self.current_sample_x, self.current_sample_y

    def _generate_centroids(self):
        """ Generates centroids

        The centroids are generated just as it's done in the parent class,
        the difference is the extra step taken to setup the drift, if there's
        any.

        To configure the drift, random offset speeds are chosen for
        ``self.num_drift_centroids`` centroids. Finally, the speed is
        normalized.

        """
        super()._generate_centroids()
        model_random_state = check_random_state(self.model_random_state)
        num_drift_centroids = self.num_drift_centroids
        self.centroid_speed = []
        if num_drift_centroids > self.n_centroids:
            num_drift_centroids = self.n_centroids

        for i in range(num_drift_centroids):
            rand_speed = []
            norm_speed = 0.0

            for j in range(self.n_num_features):
                rand_speed.append(model_random_state.rand())
                norm_speed += rand_speed[j] * rand_speed[j]

            norm_speed = np.sqrt(norm_speed)

            for j in range(self.n_num_features):
                rand_speed[j] /= norm_speed

            self.centroid_speed.append(rand_speed)
            label = random.choices(range(self.n_classes), weights=self.class_weights, k=1)
            self.centroids[i].class_label = label[0]