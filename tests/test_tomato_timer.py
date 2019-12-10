from itertools import cycle

import pytest

from CherryTomato.tomato_timer import TomatoTimer


def test_instance(tomato):
    assert tomato.state == 'tomato'
    assert tomato.seconds == 100
    assert tomato.running is False


def test_init(tomato):
    assert tomato.running is False
    assert tomato.state == 'tomato'
    assert tomato.seconds == 100


@pytest.fixture
def mock_qt_timer(mocker):
    return mocker.patch('CherryTomato.tomato_timer.Qt.QTimer')


def test_running(mock_qt_timer, tomato):
    tomato.running
    tomato.timer.isActive.assert_called_once()


@pytest.mark.parametrize('seconds,expected', [
    (62, 62),
    (-5, 0),
])
def test_seconds(tomato, seconds, expected):
    tomato.seconds = seconds
    assert tomato.seconds == expected


@pytest.mark.parametrize('seconds,progress', [
    (14, 86),
    (1, 99),
    (22.12, 77),
    (99.99, 0),
    (0, 100),
])
def test_progress(tomato, seconds, progress):
    tomato.seconds = seconds
    assert tomato.progress == progress


def test_start(mock_qt_timer, tomato):
    tomato.start()
    tomato.timer.start.assert_called_once()


def test_stop(mock_qt_timer, tomato):
    tomato.stop()
    tomato.timer.stop.assert_called_once()


@pytest.fixture
def mock_change_reset(mocker):
    return mocker.patch('CherryTomato.tomato_timer.TomatoTimer.reset')


@pytest.fixture
def mock_for_abort(mock_stop, mock_change_reset):
    pass


def test_abort(mock_for_abort, tomato):
    tomato.abort()

    tomato.stop.assert_called_once()
    tomato.reset.assert_called_once()
    assert tomato.isTomato()


@pytest.mark.parametrize('flag_value,changed', [
    (True, True),
    (False, False)
])
def test_abort_with_switch_to_tomato_flag(mock_for_abort, tomato_on_break, flag_value, changed):
    tomato_on_break.SWITCH_TO_TOMATO_ON_ABORT = flag_value

    tomato_on_break.abort()

    assert (tomato_on_break.STATE_BREAK != tomato_on_break.state) is changed


def test_create_timer(mock_qt_timer, tomato):
    assert mock_qt_timer.return_value == tomato.timer


@pytest.mark.parametrize('state,expected', [
    (TomatoTimer.STATE_TOMATO, True),
    (TomatoTimer.STATE_BREAK, False),
    (TomatoTimer.STATE_LONG_BREAK, False),
])
def test_is_tomato(tomato, state, expected):
    tomato.state = state
    assert tomato.isTomato() is expected


def test_change_state(tomato):
    for i, state in enumerate(cycle([tomato.STATE_TOMATO, tomato.STATE_BREAK])):
        assert tomato.state == state
        assert tomato.seconds == state.time
        tomato.changeState()
        if i == 10:
            break


@pytest.mark.parametrize('tomatoes,const_value,expected', [
    (0, 4, TomatoTimer.STATE_BREAK),
    (3, 4, TomatoTimer.STATE_BREAK),
    (4, 4, TomatoTimer.STATE_LONG_BREAK),
    (5, 4, TomatoTimer.STATE_BREAK),
    (12, 1, TomatoTimer.STATE_LONG_BREAK),
    (1, 10, TomatoTimer.STATE_BREAK),
    (20, 10, TomatoTimer.STATE_LONG_BREAK),
    (100, 10, TomatoTimer.STATE_LONG_BREAK),

])
def test_change_state_to_long_break(tomato, tomatoes, const_value, expected):
    tomato.TOMATOS_BEFORE_LONG_BREAK = const_value
    tomato.tomatoes = tomatoes

    tomato.changeState()

    assert tomato.state == expected
    assert tomato.seconds == expected.time


def test_reset(tomato):
    tomato.seconds = 1

    tomato.reset()

    assert tomato.seconds == tomato.STATE_TOMATO.time