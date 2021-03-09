import random


def exponential_smoothing(series, alpha):
    result = [series[0]]  # first value is same as series
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


def sse(values, predictions):
    s = 0
    for n, r in zip(values, predictions):
        s = s + (n - r)**2
    return s


def triple_exponential_smoothing(series, slen, alpha, beta, gamma, n_preds):
    result = []
    deviation = []
    seasonals = initial_seasonal_components(series, slen)
    deviations = seasonals
    for i in range(len(series)+n_preds):
        if i == 0:  # initial values
            smooth = series[0]
            trend = initial_trend(series, slen)
            result.append(series[0])
            deviation.append(0)
            continue
        if i >= len(series):  # we are forecasting
            m = i - len(series) + 1
            result.append((smooth + m*trend) + seasonals[i%slen])
            deviation.append(0)  # Unknown as we've not predicted yet
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


def fit(nums):
    # print("Fitting alpha, beta, gamma parameters for Holt-Winter forecasting with Nelder-Mead algorithm")

    # Parametri di partenza
    alpha, beta, gamma = round(random.uniform(0, 1), 3), round(random.uniform(0, 1), 3), round(random.uniform(0, 1), 3)
    # print("Starting with\n\talpha = " + str(alpha) + "\n\tbeta = " + str(beta) + "\n\tgamma = " + str(gamma))

    # Parametri Nelder-Mead
    a, g, r, s = 1., 2., -0.5, 0.5  # Parametri standard (Wikipedia)
    step = 0.001  # Step di modifica dei parametri
    noimprovthr = 10e-6  # Soglia di non miglioramento
    noimprovbrk = 10  # Ferma dopo 10 cicli dove non migliora abbastanza

    noimprov = 0  # Contatore di non miglioramento
    prev, dev = triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)
    prevbest = sse(nums, prev)  # Funzione obiettivo
    res = [[[alpha, beta, gamma], prevbest]]

    alpha += step
    prev, dev = triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)
    res.append([[alpha, beta, gamma], sse(nums, prev)])
    beta += step
    prev, dev = triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)
    res.append([[alpha, beta, gamma], sse(nums, prev)])
    gamma += step
    prev, dev = triple_exponential_smoothing(nums, 288, alpha, beta, gamma, 288)
    res.append([[alpha, beta, gamma], sse(nums, prev)])

    iterazioni = 0
    data = []
    while True:
        # Ordinamento
        res.sort(key=lambda x: x[1])
        best = res[0][1]
        # print("\r\033[F\033[K\r\033[F\033[K\r\033[F\033[K\r\033[F\033[K\r\033[F\033[K" + "{0:0=3d}".format(
        #    iterazioni) + ".\n\tBest sse: " + "{:.6f}".format(best) + "\n\talpha = " + "{:.5f}".format(
        #    res[0][0][0]) + "\n\tbeta = " + "{:.5f}".format(res[0][0][1]) + "\n\tgamma = " + "{:.5f}".format(
        #    res[0][0][2]))
        data.append([best, res[0][0][0], res[0][0][1], res[0][0][2]])

        iterazioni += 1

        if best < prevbest - noimprovthr:
            noimprov = 0
            prevbest = best
        else:
            noimprov += 1
        if noimprov >= noimprovbrk:
            break  # grafico

        # Centroide
        alpha0, beta0, gamma0 = 0., 0., 0.
        for t in res[:-1]:
            alpha0 += t[0][0] / (len(res) - 1)
            beta0 += t[0][1] / (len(res) - 1)
            gamma0 += t[0][2] / (len(res) - 1)

        # Riflessione
        alphar = abs(alpha0 + a * (alpha0 - res[-1][0][0]))
        if alphar > 1: alphar = 1
        betar = abs(beta0 + a * (beta0 - res[-1][0][1]))
        if betar > 1: betar = 1
        gammar = abs(gamma0 + a * (gamma0 - res[-1][0][2]))
        if gammar > 1: gammar = 1
        rsse = sse(nums, triple_exponential_smoothing(nums, 288, alphar, betar, gammar, 288)[0])
        if res[0][1] <= rsse < res[-2][1]:
            del res[-1]
            res.append([[alphar, betar, gammar], rsse])
            continue

        # Espansione
        if rsse < res[0][1]:
            alphae = abs(alpha0 + g * (alpha0 - res[-1][0][0]))
            if alphae > 1: alphae = 1
            betae = abs(beta0 + g * (beta0 - res[-1][0][1]))
            if betae > 1: betae = 1
            gammae = abs(gamma0 + g * (gamma0 - res[-1][0][2]))
            if gammae > 1: gammae = 1
            esse = sse(nums, triple_exponential_smoothing(nums, 288, alphae, betae, gammae, 288)[0])
            if esse < rsse:
                del res[-1]
                res.append([[alphae, betae, gammae], esse])
                continue
            else:
                del res[-1]
                res.append([[alphar, betar, gammar], rsse])
                continue

        # Contrazione
        alphac = abs(alpha0 + r * (alpha0 - res[-1][0][0]))
        if alphac > 1: alphac = 1
        betac = abs(beta0 + r * (beta0 - res[-1][0][1]))
        if betac > 1: betac = 1
        gammac = abs(gamma0 + r * (gamma0 - res[-1][0][2]))
        if gammac > 1: gammac = 1
        csse = sse(nums, triple_exponential_smoothing(nums, 288, alphac, betac, gammac, 288)[0])
        if csse < res[-1][1]:
            del res[-1]
            res.append([[alphac, betac, gammac], csse])
            continue

        # Riduzione
        alpha1 = res[0][0][0]
        beta1 = res[0][0][1]
        gamma1 = res[0][0][2]
        nres = []
        for t in res:
            ridalpha = abs(alpha1 + s * (t[0][0] - alpha1))
            if ridalpha > 1: ridalpha = 1
            ridbeta = abs(beta1 + s * (t[0][1] - beta1))
            if ridbeta > 1: ridbeta = 1
            ridgamma = abs(gamma1 + s * (t[0][2] - gamma1))
            if ridgamma > 1: ridgamma = 1
            ridsse = sse(nums, triple_exponential_smoothing(nums, 288, ridalpha, ridbeta, ridgamma, 288)[0])
            nres.append([[ridalpha, ridbeta, ridgamma], ridsse])
        res = nres

    # stralpha = "{:.5f}".format(alpha)
    # strbeta = "{:.5f}".format(beta)
    # strgamma = "{:.5f}".format(gamma)
    # print("Dopo " + str(iterazioni) + " iterazioni ho trovato:\n\talpha = " +
    #      stralpha + "\n\tbeta = " + strbeta + "\n\tgamma = " + strgamma)
    return res[0][0][0], res[0][0][1], res[0][0][2], res[0][1]


def rsi(nums, N):
	RSIlist = []
	count = 0
	prev = 0
	sumD = 0
	sumU = 0
	prevn = 0
	for n in nums:
		if count < N:
			if n > prevn: sumU = sumU + (n - prevn)
			if n < prevn: sumD = sumD + (prevn - n)
			avgU = sumU/N
			avgD = sumD/N
			RSIlist.append(0)
			count += 1
			prevn = n
		else:
			if n > prevn: avgU = ((avgU * (N-1)) + (n - prevn))/N
			if n < prevn: avgD = ((avgD * (N-1)) + (prevn - n))/N
			RS = avgU/avgD
			RSI = 100 - 100/(1+RS)
			RSIlist.append(RSI)
			prevn = n
	return RSIlist
