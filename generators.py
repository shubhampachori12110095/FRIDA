from __future__ import division

import numpy as np
from scipy import linalg
import datetime
import os
import matplotlib.pyplot as plt

from utils import polar2cart


def gen_sig_at_mic(sigmak2_k, phi_k, pos_mic_x,
                   pos_mic_y, omega_band, sound_speed,
                   SNR, Ns=256):
    """
    generate complex base-band signal received at microphones
    :param sigmak2_k: the variance of the circulant complex Gaussian signal
                emitted by the K sources
    :param phi_k: source locations (azimuths)
    :param pos_mic_x: a vector that contains microphones' x coordinates
    :param pos_mic_y: a vector that contains microphones' y coordinates
    :param omega_band: mid-band (ANGULAR) frequency [radian/sec]
    :param sound_speed: speed of sound
    :param SNR: SNR for the received signal at microphones
    :param Ns: number of snapshots used to estimate the covariance matrix
    :return: y_mic: received (complex) signal at microphones
    """
    num_mic = pos_mic_x.size
    xk, yk = polar2cart(1, phi_k)  # source locations in cartesian coordinates
    # reshape to use broadcasting
    xk = np.reshape(xk, (1, -1), order='F')
    yk = np.reshape(yk, (1, -1), order='F')
    pos_mic_x = np.reshape(pos_mic_x, (-1, 1), order='F')
    pos_mic_y = np.reshape(pos_mic_y, (-1, 1), order='F')

    t = np.reshape(np.linspace(0, 10 * np.pi, num=Ns), (1, -1), order='F')
    K = sigmak2_k.size
    sigmak2_k = np.reshape(sigmak2_k, (-1, 1), order='F')

    # x_tilde_k size: K x length_of_t
    # circular complex Gaussian process
    x_tilde_k = np.sqrt(sigmak2_k / 2.) * (np.random.randn(K, Ns) + 1j *
                                           np.random.randn(K, Ns))
    y_mic = np.dot(np.exp(-1j * (xk * pos_mic_x + yk * pos_mic_y) / (sound_speed / omega_band)),
                   x_tilde_k * np.exp(1j * omega_band * t))
    signal_energy = linalg.norm(y_mic, 'fro') ** 2
    noise_energy = signal_energy / 10 ** (SNR * 0.1)
    sigma2_noise = noise_energy / (Ns * num_mic)
    noise = np.sqrt(sigma2_noise / 2.) * (np.random.randn(*y_mic.shape) + 1j *
                                          np.random.randn(*y_mic.shape))
    y_mic_noisy = y_mic + noise
    return y_mic_noisy, y_mic


def gen_visibility(alphak, phi_k, pos_mic_x, pos_mic_y):
    """
    generate visibility from the Dirac parameter and microphone array layout
    :param alphak: Diracs' amplitudes
    :param phi_k: azimuths
    :param pos_mic_x: a vector that contains microphones' x coordinates
    :param pos_mic_y: a vector that contains microphones' y coordinates
    :return:
    """
    xk, yk = polar2cart(1, phi_k)
    num_mic = pos_mic_x.size
    visi = np.zeros((num_mic, num_mic), dtype=complex)
    for q in xrange(num_mic):
        p_x_outer = pos_mic_x[q]
        p_y_outer = pos_mic_y[q]
        for qp in xrange(num_mic):
            p_x_qqp = p_x_outer - pos_mic_x[qp]  # a scalar
            p_y_qqp = p_y_outer - pos_mic_y[qp]  # a scalar
            visi[qp, q] = np.dot(np.exp(-1j * (xk * p_x_qqp + yk * p_y_qqp)), alphak)
    return visi


def gen_dirty_img(visi, pos_mic_x, pos_mic_y, omega_band, sound_speed, phi_plt):
    """
    Compute the dirty image associated with the given measurements. Here the Fourier transform
    that is not measured by the microphone array is taken as zero.
    :param visi: the measured visibilites
    :param pos_mic_x: a vector contains microphone array locations (x-coordinates)
    :param pos_mic_y: a vector contains microphone array locations (y-coordinates)
    :param omega_band: mid-band (ANGULAR) frequency [radian/sec]
    :param sound_speed: speed of sound
    :param phi_plt: plotting grid (azimuth on the circle) to show the dirty image
    :return:
    """
    img = np.zeros(phi_plt.size, dtype=complex)
    x_plt, y_plt = polar2cart(1, phi_plt)
    num_mic = pos_mic_x.size

    pos_mic_x_normalised = pos_mic_x / (sound_speed / omega_band)
    pos_mic_y_normalised = pos_mic_y / (sound_speed / omega_band)

    count_visi = 0
    for q in xrange(num_mic):
        p_x_outer = pos_mic_x_normalised[q]
        p_y_outer = pos_mic_y_normalised[q]
        for qp in xrange(num_mic):
            if not q == qp:
                p_x_qqp = p_x_outer - pos_mic_x_normalised[qp]  # a scalar
                p_y_qqp = p_y_outer - pos_mic_y_normalised[qp]  # a scalar
                img += visi[count_visi] * \
                       np.exp(1j * (p_x_qqp * x_plt + p_y_qqp * y_plt))
                count_visi += 1
    return img / (num_mic * (num_mic - 1))


def gen_mic_array_2d(radius_array, num_mic=3, save_layout=True,
                     divi=3, plt_layout=False, **kwargs):
    """
    generate microphone array layout randomly
    :param radius_array: microphones are contained within a cirle of this radius
    :param num_mic: number of microphones
    :param save_layout: whether to save the microphone array layout or not
    :return:
    """
    # pos_array_norm = np.linspace(0, radius_array, num=num_mic, dtype=float)
    # pos_array_angle = np.linspace(0, 5 * np.pi, num=num_mic, dtype=float)
    num_seg = np.ceil(num_mic / divi)
    # radius_stepsize = radius_array / num_seg

    # pos_array_norm = np.append(np.repeat((np.arange(num_seg) + 1) * radius_stepsize,
    #                                      divi)[:num_mic-1], 0)
    pos_array_norm = np.linspace(0, radius_array, num=num_mic, endpoint=False)

    # pos_array_angle = np.append(np.tile(np.pi * 2 * np.arange(divi) / divi, num_seg)[:num_mic-1], 0)
    pos_array_angle = np.reshape(np.tile(np.pi * 2 * np.arange(divi) / divi, num_seg),
                                 (divi, -1), order='F') + \
                      np.linspace(0, 2 * np.pi / divi,
                                  num=num_seg, endpoint=False)[np.newaxis, :]
    pos_array_angle = np.insert(pos_array_angle.flatten('F')[:num_mic - 1], 0, 0)

    pos_array_angle += np.random.rand() * np.pi / divi
    # pos_array_norm = np.random.rand(num_mic) * radius_array
    # pos_array_angle = 2 * np.pi * np.random.rand(num_mic)

    pos_mic_x = pos_array_norm * np.cos(pos_array_angle)
    pos_mic_y = pos_array_norm * np.sin(pos_array_angle)

    layout_time_stamp = datetime.datetime.now().strftime('%d-%m')
    if save_layout:
        directory = './data/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_name = directory + 'mic_layout_' + layout_time_stamp + '.npz'
        np.savez(file_name, pos_mic_x=pos_mic_x, pos_mic_y=pos_mic_y,
                 layout_time_stamp=layout_time_stamp)

    if plt_layout:
        plt.figure(figsize=(2.5, 2.5), dpi=90)
        plt.plot(pos_mic_x, pos_mic_y, 'x')
        plt.axis('image')
        plt.xlim([-radius_array, radius_array])
        plt.ylim([-radius_array, radius_array])
        plt.title('microphone array layout', fontsize=11)

        if 'save_fig' in kwargs:
            save_fig = kwargs['save_fig']
        else:
            save_fig = False
        if 'fig_dir' in kwargs and save_fig:
            fig_dir = kwargs['fig_dir']
        else:
            fig_dir = './result/'
        if save_fig:
            if not os.path.exists(fig_dir):
                os.makedirs(fig_dir)
            fig_name = (fig_dir + 'polar_numMic_{0}_layout' +
                        layout_time_stamp + '.pdf').format(repr(num_mic))
            plt.savefig(fig_name, format='pdf', dpi=300, transparent=True)

            # plt.show()
    return pos_mic_x, pos_mic_y, layout_time_stamp


def gen_diracs_param(K, positive_amp=True, log_normal_amp=False,
                     semicircle=True, save_param=True):
    """
    randomly generate Diracs' parameters
    :param K: number of Diracs
    :param positive_amp: whether Diracs have positive amplitudes or not
    :param log_normal_amp: whether the Diracs amplitudes follow log-normal distribution.
    :param semicircle: whether the Diracs are located on half of the circle or not.
    :param save_param: whether to save the Diracs' parameter or not.
    :return:
    """
    # amplitudes
    if log_normal_amp:
        positive_amp = True
    if not positive_amp:
        alpha_ks = np.sign(np.random.randn(K)) * (0.7 + 0.6 * (np.random.rand(K) - 0.5) / 1.)
    elif log_normal_amp:
        alpha_ks = np.random.lognormal(mean=np.log(2), sigma=0.7, size=K)
    else:
        alpha_ks = 0.7 + 0.6 * (np.random.rand(K) - 0.5) / 1.

    # location on the circle (S^1)
    if semicircle:
        factor = 1
    else:
        factor = 2

    exp_rnd = np.random.exponential(1. / (K - 1), K - 1)
    min_sep = 1. / 30
    phi_ks = np.cumsum(min_sep + (1 - (K - 1) * min_sep) *
                       (1. - 0.1 * np.random.rand(1, 1)) /
                       np.sum(exp_rnd) * exp_rnd)
    phi_ks = factor * np.pi * np.append(phi_ks, np.random.rand() * phi_ks[0] / 2.)

    time_stamp = datetime.datetime.now().strftime('%d-%m_%H_%M')
    if save_param:
        if not os.path.exists('./data/'):
            os.makedirs('./data/')
        file_name = './data/polar_Dirac_' + time_stamp + '.npz'
        np.savez(file_name, alpha_ks=alpha_ks,
                 phi_ks=phi_ks, K=K, time_stamp=time_stamp)
    return alpha_ks, phi_ks, time_stamp


# # if uncommented, use: from tools_fri_doa_plane import extract_off_diag
# def add_noise(visi_noiseless, var_noise, num_mic, Ns=256):
#     """
#     add noise to the noiselss visibility
#     :param visi_noiseless: noiseless visibilities
#     :param var_noise: variance of noise
#     :param num_mic: number of microphones
#     :param Ns: number of samples used to estimate the covariance matrix
#     :return:
#     """
#     sigma_mtx = visi_noiseless + var_noise * np.eye(*visi_noiseless.shape)
#     wischart_mtx = np.kron(sigma_mtx.conj(), sigma_mtx) / Ns
#     # the noise vairance matrix is given by the Cholesky decomposition
#     noise_conv_mtx_sqrt = np.linalg.cholesky(wischart_mtx)
#     visi_noiseless_vec = np.reshape(visi_noiseless, (-1, 1), order='F')
#     noise = np.dot(noise_conv_mtx_sqrt,
#                    np.random.randn(*visi_noiseless_vec.shape) +
#                    1j * np.random.randn(*visi_noiseless_vec.shape)) / np.sqrt(2)
#     # a matrix form
#     visi_noisy = np.reshape(visi_noiseless_vec + noise, visi_noiseless.shape, order='F')
#     # extract the off-diagonal entries
#     visi_noisy = extract_off_diag(visi_noisy)
#     visi_noiseless_off_diag = extract_off_diag(visi_noiseless)
#     # calculate the equivalent SNR
#     noise = visi_noisy - visi_noiseless_off_diag
#     P = 20 * np.log10(linalg.norm(visi_noiseless_off_diag) / linalg.norm(noise))
#     return visi_noisy, P, noise, visi_noiseless_off_diag