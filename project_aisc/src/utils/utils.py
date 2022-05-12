
def save_results(score,model,evaluations,arg_save,elements,materials):
    """Save results and model

    Save score, model and evaluations if specified through cli.
    Evaluations is a csv file containig an index, the observed critical temperature
    and the relative predictions. The index is referred to the selected materials.

    Args:
        - score: list containing model's metrics evaluated on test set
        - model: tf.keras.model that will be saved
        - evaluations: list containing Y_test and the relative predictions
        - arg_save: string or list to target what to save. It can contain:
           - 'all' -> save score, model, evaluations
           - 'score' -> save score
           - 'model' -> save model with SavedModel format
           - 'evaluations' -> save indexs, tests and predictions

    """
    import os
    import datetime
    import csv
    import pandas as pd

    date = datetime.datetime.now()

    directory = '/home/claudio/AISC/project_aisc/data/experiments/experiments_'+date.strftime("%d")+"-"+date.strftime("%m")
    #Flag to check if an experiment and relative directory containing that data is alredy present
    today_experiments = os.path.isdir(directory)

    if not today_experiments:
        os.makedirs(directory)
    #count the number of experiments done for the day
    n_experiment_per_day = len([name for name in os.listdir(directory)])
    #each experiment has their own folder
    experiment_name = directory + '/experiment' + "-" + str(n_experiment_per_day)
    current_experiment = os.path.isdir(experiment_name)

    if not current_experiment:
        os.makedirs(experiment_name)

    if 'all' in arg_save or 'score' in arg_save:
        with open(experiment_name + '/score.csv', mode='a') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([metric.name for metric in model.metrics])
            csv_writer.writerow(score)

    if 'all' in arg_save or 'model' in arg_save:
        model.save(experiment_name + '/model')

    if 'all' in arg_save or 'test' in arg_save:
        ob_and_pred = pd.DataFrame({'observed' : evaluations[0].values,'predicted': [value[0] for value in evaluations[1]]},index = evaluations[0].index)
        ob_and_pred.to_csv(experiment_name + '/evaluations.csv')
    if 'all' in arg_save or 'elements' in arg_save:
        elements.to_csv(experiment_name + '/elements.csv')
    if 'all' in arg_save or 'materials' in arg_save:
        materials.to_csv(experiment_name + '/materials.csv')