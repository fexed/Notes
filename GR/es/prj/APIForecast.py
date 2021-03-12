import random
import sys


def exponential_smoothing(series, alpha):
    result = [series[0]]  # first value is same as series
    for i in range(1, len(series)):
        result.append(alpha * series[i] + (1 - alpha) * result[i - 1])
    # Now append the prediction
    result.append(alpha * series[i] + (1 - alpha) * result[i])
    return result


def double_exponential_smoothing(series, alpha, beta):
    result = [series[0]]
    for i in range(1, len(series) + 2):
        if i == 1:
            level, trend = series[0], series[1] - series[0]
        if i >= len(series):  # we are forecasting
            value = result[-1]
        else:
            value = series[i]
        last_level, level = level, alpha * value + (1 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1 - beta) * trend
        result.append(level + trend)
    return result


def initial_trend(series, slen):
    sum = 0.0
    for i in range(slen):
        sum += float(series[i + slen] - series[i]) / slen
    return sum / slen


def initial_seasonal_components(series, slen):
    seasonals = {}
    season_averages = []
    n_seasons = int(len(series) / slen)
    # compute season averages
    for j in range(n_seasons):
        season_averages.append(sum(series[slen * j:slen * j + slen]) / float(slen))
    # compute initial values

    for i in range(slen):
        sum_of_vals_over_avg = 0.0
        for j in range(n_seasons):
            sum_of_vals_over_avg += series[slen * j + i] - season_averages[j]
        seasonals[i] = sum_of_vals_over_avg / n_seasons
    return seasonals


def sse(values, predictions):
    try:
        s = 0
        for n, r in zip(values, predictions):
            s = s + (n - r) ** 2
        return s
    except OverflowError:
        return sys.float_info.max


def triple_exponential_smoothing(series, slen, alpha, beta, gamma, n_preds):
    result = []
    deviation = []
    ubound, lbound = [], []
    seasonals = initial_seasonal_components(series, slen)
    deviations = seasonals
    for i in range(len(series) + n_preds):
        if i == 0:  # initial values
            smooth = series[0]
            trend = initial_trend(series, slen)
            result.append(series[0])
            deviation.append(0)
            ubound.append(result[0] + 2.5 * deviation[0])
            lbound.append(result[0] - 2.5 * deviation[0])
            continue
        if i >= len(series):  # we are forecasting
            m = i - len(series) + 1
            result.append((smooth + m * trend) + seasonals[i % slen])
            deviation.append(0)  # Unknown as we've not predicted yet
        else:
            val = series[i]
            last_smooth, smooth = smooth, alpha * (val - seasonals[i % slen]) + (1 - alpha) * (smooth + trend)
            last_trend, trend = trend, beta * (smooth - last_smooth) + (1 - beta) * trend
            seasonals[i % slen] = gamma * (val - smooth) + (1 - gamma) * seasonals[i % slen]
            prediction = smooth + trend + seasonals[i % slen]
            result.append(prediction)
#           deviations[i % slen] = gamma * abs(val - prediction) + (1 - gamma) * deviation[-1]
            deviation.append(gamma*abs(val - prediction) + (1-gamma)*deviation[-1])
        ubound.append(result[-1] + 2.5 * deviation[-1])
        lbound.append(result[-1] - 2.5 * deviation[-1])
    return result, deviation, ubound, lbound


def fit_triple(nums, season):
    # Fitting alpha, beta, gamma parameters for Holt-Winter forecasting with Nelder-Mead algorithm

    # Starting parameters
    alpha, beta, gamma = round(random.uniform(0, 1), 3), round(random.uniform(0, 1), 3), round(random.uniform(0, 1), 3)

    # Nelder-Mead parameters
    a, g, r, s = 1., 2., -0.5, 0.5  # Standard parameters (Wikipedia)
    step = 0.001  # Increment step
    noimprovthr = 10e-6  # Non improvement threshold
    noimprovbrk = 10  # Stop after 10 iterations without improvement

    noimprov = 0  # Non improvement counter
    prev, dev, ubound, lbound = triple_exponential_smoothing(nums, season, alpha, beta, gamma, season)
    prevbest = sse(nums, prev)  # Target function
    res = [[[alpha, beta, gamma], prevbest]]

    alpha += step
    prev, dev, ubound, lbound = triple_exponential_smoothing(nums, season, alpha, beta, gamma, season)
    res.append([[alpha, beta, gamma], sse(nums, prev)])
    beta += step
    prev, dev, ubound, lbound = triple_exponential_smoothing(nums, season, alpha, beta, gamma, season)
    res.append([[alpha, beta, gamma], sse(nums, prev)])
    gamma += step
    prev, dev, ubound, lbound = triple_exponential_smoothing(nums, season, alpha, beta, gamma, season)
    res.append([[alpha, beta, gamma], sse(nums, prev)])

    iterazioni = 0
    while True:
        # Ordering
        res.sort(key=lambda x: x[1])
        best = res[0][1]

        iterazioni += 1

        if best < prevbest - noimprovthr:
            noimprov = 0
            prevbest = best
        else:
            noimprov += 1
        if noimprov >= noimprovbrk:
            break  # grafico

        # Centroid
        alpha0, beta0, gamma0 = 0., 0., 0.
        for t in res[:-1]:
            alpha0 += t[0][0] / (len(res) - 1)
            beta0 += t[0][1] / (len(res) - 1)
            gamma0 += t[0][2] / (len(res) - 1)

        # Reflection
        alphar = alpha0 + a * (alpha0 - res[-1][0][0])
        betar = beta0 + a * (beta0 - res[-1][0][1])
        gammar = gamma0 + a * (gamma0 - res[-1][0][2])
        rsse = sse(nums, triple_exponential_smoothing(nums, season, alphar, betar, gammar, season)[0])
        if res[0][1] <= rsse < res[-2][1]:
            del res[-1]
            if (alphar < 0 or alphar > 1) or (betar < 0 or betar > 1) or (gammar < 0 or gammar > 1):
                rsse += 1000
                rsse *= 1000
            res.append([[alphar, betar, gammar], rsse])
            continue

        # Expansion
        if rsse < res[0][1]:
            alphae = alpha0 + g * (alpha0 - res[-1][0][0])
            betae = beta0 + g * (beta0 - res[-1][0][1])
            gammae = gamma0 + g * (gamma0 - res[-1][0][2])
            esse = sse(nums, triple_exponential_smoothing(nums, season, alphae, betae, gammae, season)[0])
            if esse < rsse:
                del res[-1]
                if (alphae < 0 or alphae > 1) or (betae < 0 or betae > 1) or (gammae < 0 or gammae > 1):
                    esse += 1000
                    esse *= 1000
                res.append([[alphae, betae, gammae], esse])
                continue
            else:
                del res[-1]
                if (alphar < 0 or alphar > 1) or (betar < 0 or betar > 1) or (gammar < 0 or gammar > 1):
                    rsse += 1000
                    rsse *= 1000
                res.append([[alphar, betar, gammar], rsse])
                continue

        # Contraction
        alphac = alpha0 + r * (alpha0 - res[-1][0][0])
        betac = beta0 + r * (beta0 - res[-1][0][1])
        gammac = gamma0 + r * (gamma0 - res[-1][0][2])
        csse = sse(nums, triple_exponential_smoothing(nums, season, alphac, betac, gammac, season)[0])
        if csse < res[-1][1]:
            del res[-1]
            if (alphac < 0 or alphac > 1) or (betac < 0 or betac > 1) or (gammac < 0 or gammac > 1):
                csse += 1000
                csse *= 1000
            res.append([[alphac, betac, gammac], csse])
            continue

        # Reduction
        alpha1 = res[0][0][0]
        beta1 = res[0][0][1]
        gamma1 = res[0][0][2]
        nres = []
        for t in res:
            ridalpha = alpha1 + s * (t[0][0] - alpha1)
            ridbeta = beta1 + s * (t[0][1] - beta1)
            ridgamma = gamma1 + s * (t[0][2] - gamma1)
            ridsse = sse(nums, triple_exponential_smoothing(nums, season, ridalpha, ridbeta, ridgamma, season)[0])
            if (ridalpha < 0 or ridalpha > 1) or (ridbeta < 0 or ridbeta > 1) or (ridgamma < 0 or ridgamma > 1):
                ridsse += 1000
                ridsse *= 1000
            nres.append([[ridalpha, ridbeta, ridgamma], ridsse])
        res = nres

    return res[0][0][0], res[0][0][1], res[0][0][2], res[0][1]


def fit_double(nums):
    # Fitting alpha, beta parameters for double exponential forecasting with Nelder-Mead algorithm

    # Starting parameters
    alpha, beta = round(random.uniform(0, 1), 3), round(random.uniform(0, 1), 3)

    # Nelder-Mead parameters
    a, g, r, s = 1., 2., -0.5, 0.5  # Standard parameters (Wikipedia)
    step = 0.001  # Increment step
    noimprovthr = 10e-6  # Non improvement threshold
    noimprovbrk = 10  # Stop after 10 iterations without improvement

    noimprov = 0  # Non improvement counter
    prev = double_exponential_smoothing(nums, alpha, beta)
    prevbest = sse(nums, prev)  # Target function
    res = [[[alpha, beta], prevbest]]

    alpha += step
    prev = double_exponential_smoothing(nums, alpha, beta)
    res.append([[alpha, beta], sse(nums, prev)])
    beta += step
    prev = double_exponential_smoothing(nums, alpha, beta)
    res.append([[alpha, beta], sse(nums, prev)])

    iterazioni = 0
    while True:
        # Ordering
        res.sort(key=lambda x: x[1])
        best = res[0][1]

        iterazioni += 1

        if best < prevbest - noimprovthr:
            noimprov = 0
            prevbest = best
        else:
            noimprov += 1
        if noimprov >= noimprovbrk:
            break  # grafico

        # Centroid
        alpha0, beta0 = 0., 0.
        for t in res[:-1]:
            alpha0 += t[0][0] / (len(res) - 1)
            beta0 += t[0][1] / (len(res) - 1)

        # Reflection
        alphar = abs(alpha0 + a * (alpha0 - res[-1][0][0]))
        if alphar > 1: alphar = 1
        betar = abs(beta0 + a * (beta0 - res[-1][0][1]))
        if betar > 1: betar = 1
        rsse = sse(nums, double_exponential_smoothing(nums, alphar, betar))
        if res[0][1] <= rsse < res[-2][1]:
            del res[-1]
            res.append([[alphar, betar], rsse])
            continue

        # Expansion
        if rsse < res[0][1]:
            alphae = abs(alpha0 + g * (alpha0 - res[-1][0][0]))
            if alphae > 1: alphae = 1
            betae = abs(beta0 + g * (beta0 - res[-1][0][1]))
            if betae > 1: betae = 1
            esse = sse(nums, double_exponential_smoothing(nums, alphae, betae))
            if esse < rsse:
                del res[-1]
                res.append([[alphae, betae], esse])
                continue
            else:
                del res[-1]
                res.append([[alphar, betar], rsse])
                continue

        # Contraction
        alphac = abs(alpha0 + r * (alpha0 - res[-1][0][0]))
        if alphac > 1: alphac = 1
        betac = abs(beta0 + r * (beta0 - res[-1][0][1]))
        if betac > 1: betac = 1
        csse = sse(nums, double_exponential_smoothing(nums, alphac, betac))
        if csse < res[-1][1]:
            del res[-1]
            res.append([[alphac, betac], csse])
            continue

        # Reduction
        alpha1 = res[0][0][0]
        beta1 = res[0][0][1]
        nres = []
        for t in res:
            ridalpha = abs(alpha1 + s * (t[0][0] - alpha1))
            if ridalpha > 1: ridalpha = 1
            ridbeta = abs(beta1 + s * (t[0][1] - beta1))
            if ridbeta > 1: ridbeta = 1
            ridsse = sse(nums, double_exponential_smoothing(nums, ridalpha, ridbeta))
            nres.append([[ridalpha, ridbeta], ridsse])
        res = nres

    return res[0][0][0], res[0][0][1], res[0][1]


def fit_single(nums):
    # Fitting alpha parameter for single exponential forecasting with Nelder-Mead algorithm

    # Starting parameter
    alpha = round(random.uniform(0, 1), 3)

    # Nelder-Mead parameters
    a, g, r, s = 1., 2., -0.5, 0.5  # Standard parameters (Wikipedia)
    step = 0.001  # Increment step
    noimprovthr = 10e-6  # Non improvement threshold
    noimprovbrk = 10  # Stop after 10 iterations without improvement

    noimprov = 0  # Non improvement counter
    prev = exponential_smoothing(nums, alpha)
    prevbest = sse(nums, prev)  # Target function
    res = [[[alpha], prevbest]]

    alpha += step
    prev = exponential_smoothing(nums, alpha)
    res.append([[alpha], sse(nums, prev)])

    iterazioni = 0
    while True:
        # Ordering
        res.sort(key=lambda x: x[1])
        best = res[0][1]

        iterazioni += 1

        if best < prevbest - noimprovthr:
            noimprov = 0
            prevbest = best
        else:
            noimprov += 1
        if noimprov >= noimprovbrk:
            break  # grafico

        # Centroid
        alpha0 = 0.
        for t in res[:-1]:
            alpha0 += t[0][0] / (len(res) - 1)

        # Reflection
        alphar = abs(alpha0 + a * (alpha0 - res[-1][0][0]))
        if alphar > 1: alphar = 1
        rsse = sse(nums, exponential_smoothing(nums, alphar))
        if res[0][1] <= rsse < res[-2][1]:
            del res[-1]
            res.append([[alphar], rsse])
            continue

        # Expansion
        if rsse < res[0][1]:
            alphae = abs(alpha0 + g * (alpha0 - res[-1][0][0]))
            if alphae > 1: alphae = 1
            esse = sse(nums, exponential_smoothing(nums, alphae))
            if esse < rsse:
                del res[-1]
                res.append([[alphae], esse])
                continue
            else:
                del res[-1]
                res.append([[alphar], rsse])
                continue

        # Contraction
        alphac = abs(alpha0 + r * (alpha0 - res[-1][0][0]))
        if alphac > 1: alphac = 1
        csse = sse(nums, exponential_smoothing(nums, alphac))
        if csse < res[-1][1]:
            del res[-1]
            res.append([[alphac], csse])
            continue

        # Reduction
        alpha1 = res[0][0][0]
        nres = []
        for t in res:
            ridalpha = abs(alpha1 + s * (t[0][0] - alpha1))
            if ridalpha > 1: ridalpha = 1
            ridsse = sse(nums, exponential_smoothing(nums, ridalpha))
            nres.append([[ridalpha], ridsse])
        res = nres

    return res[0][0][0], res[0][1]


def rsi(nums, N):
    RSIlist = []
    count = 0
    sumD = 0
    sumU = 0
    prevn = 0
    for n in nums:
        if count < N:
            if n > prevn: sumU = sumU + (n - prevn)
            if n < prevn: sumD = sumD + (prevn - n)
            avgU = sumU / N
            avgD = sumD / N
            RSIlist.append(0)
            count += 1
            prevn = n
        else:
            if n > prevn: avgU = ((avgU * (N - 1)) + (n - prevn)) / N
            if n < prevn: avgD = ((avgD * (N - 1)) + (prevn - n)) / N
            RS = avgU / avgD
            RSI = 100 - 100 / (1 + RS)
            RSIlist.append(RSI)
            prevn = n
    return RSIlist
