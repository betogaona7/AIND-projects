import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        
        BIC_score = float("inf")
        best_num_components = self.n_constant
        
        for components in range(self.min_n_components, self.max_n_components + 1):
            try:
                model = GaussianHMM(n_components=components, n_iter=1000).fit(self.X, self.lengths)

                n_features = self.X.shape[1]
                logL = model.score(self.X, self.lengths)
                p = ((components**2.) + (2. * components * (n_features - 1)))
                logN = np.log(len(self.lengths))

                BIC = -2 * logL + p * logN

                if BIC < BIC_score:
                    best_num_components = components
                    BIC_score = BIC
            except:
                pass
                
        return self.base_model(best_num_components)

class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    https://pdfs.semanticscholar.org/ed3d/7c4a5f607201f3848d4c02dd9ba17c791fc2.pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        
        # log(P(X(i))) = logL, score that is returned from the model 
        # SUM(log(P(X(all but i))) = antilogL, score when evaluating the model on all words other than the word for which
        #                            we are training this particular model. 
        # M = Total quantify words
      
        DIC_score = float("-inf")
        best_num_components = self.n_constant
        
        for components in range(self.min_n_components, self.max_n_components + 1):
            try:
                model = self.base_model(components)
                logL = model.score(self.X, self.lengths)
                M = len(self.words)
                antilogL = 0
                
                for word in self.words:
                    X, lengths = self.hwords[word]
                    antilogL += model.score(X, lengths)
                
                DIC = logL - 1/(M-1) * antilogL
                
                if DIC > DIC_score:
                    best_num_components = components
                    DIC_score = DIC
            except:
                pass
            
        return self.base_model(best_num_components)

    
class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        
        CV_score = float("-inf")
        best_num_components = self.n_constant
        
        for components in range(self.min_n_components, self.max_n_components + 1):
            if len(self.sequences) <= 1:
                continue
            try:
                split_method = KFold()    
                logL_scores = []
                for cv_train_idx, cv_test_idx in split_method.split(self.sequences):
                    
                    X_train, lengths_train = combine_sequences(cv_train_idx, self.sequences)
                    X_test, lengths_test = combine_sequences(cv_test_idx, self.sequences)
                    
                    model = GaussianHMM(n_components=components, n_iter=1000).fit(X_train, lengths_train)
                    logL_scores.append(model.score(X_test, lengths_test))
                    
                if np.mean(logL_scores) > CV_score:
                    best_num_components = components
                    CV_score = np.mean(logL_scores)
            except:
                pass 
        
        return self.base_model(best_num_components)