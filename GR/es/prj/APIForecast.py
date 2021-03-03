

def exponential_smoothing(series, alpha):
    result = [series[0]] # first value is same as series
    for i in range(1, len(series)):
        result.append(alpha * series[i] + (1 - alpha) * result[i-1])
    # Now append the prediction
    result.append(alpha * series[i] + (1 - alpha) * result[i])
    return result




def double_exponential_smoothing(series, alpha, beta):
    result = [series[0]]
    for i in range(1, len(series)+2):
        if i == 1:
            level, trend = series[0], series[1] - series[0]
        if i >= len(series): # we are forecasting
            value = result[-1]
        else:
            value = series[i]
        last_level, level = level, alpha*value + (1-alpha)*(level+trend)
        trend = beta*(level-last_level) + (1-beta)*trend
        result.append(level+trend)
    return result





def initial_trend(series, slen):
    sum = 0.0
    for i in range(slen):
        sum += float(series[i+slen] - series[i]) / slen
    return sum / slen


def initial_seasonal_components(series, slen):
    seasonals = {}
    season_averages = []
    n_seasons = int(len(series)/slen)
    # compute season averages
    for j in range(n_seasons):
        season_averages.append(sum(series[slen*j:slen*j+slen])/float(slen))
    # compute initial values

    for i in range(slen):
        sum_of_vals_over_avg = 0.0
        for j in range(n_seasons):
            sum_of_vals_over_avg += series[slen*j+i]-season_averages[j]
        seasonals[i] = sum_of_vals_over_avg/n_seasons
    return seasonals



def triple_exponential_smoothing(series, slen, alpha, beta, gamma, n_preds):
    result = []
    deviation = []
    seasonals = initial_seasonal_components(series, slen)
    deviations = seasonals
    for i in range(len(series)+n_preds):
        if i == 0: # initial values
            smooth = series[0]
            trend = initial_trend(series, slen)
            result.append(series[0])
            deviation.append(0)
            continue
        if i >= len(series): # we are forecasting
            m = i - len(series) + 1
            result.append((smooth + m*trend) + seasonals[i%slen])
            deviation.append(0) # Unknown as we've not predicted yet
        else:
            val = series[i]
            last_smooth, smooth = smooth, alpha*(val-seasonals[i%slen]) + (1-alpha)*(smooth+trend)
            trend = beta * (smooth-last_smooth) + (1-beta)*trend
            seasonals[i%slen] = gamma*(val-smooth) + (1-gamma)*seasonals[i%slen]
            prediction = smooth+trend+seasonals[i%slen]
            result.append(prediction)
            deviations[i%slen] = gamma*abs(val-prediction) + (1-gamma)*deviations[i%slen]
            deviation.append(abs(deviations[i%slen]))
    return result,deviation