import pickle
import threading
from typing import List, Dict

import vent
import vent.controller.control_module
from vent.common.message import ControlSetting, Alarm
from vent.common.message import SensorValue
from vent.common.values import ValueName
from vent.coordinator.process_manager import ProcessManager
from vent.coordinator.rpc import get_rpc_client


class CoordinatorBase:
    def __init__(self, sim_mode=False):
        # get_ui_control_module handles single_process flag
        # self.lock = threading.Lock()
        pass

    # TODO: do we still need this
    # def get_msg_timestamp(self):
    #     # return timestamp of last message
    #     with self.lock:
    #         last_message_timestamp = self.last_message_timestamp
    #     return last_message_timestamp

    def get_sensors(self) -> Dict[ValueName, SensorValue]:
        pass

    def get_active_alarms(self) -> Dict[str, Alarm]:
        pass

    def get_logged_alarms(self) -> List[Alarm]:
        pass

    def clear_logged_alarms(self):
        pass

    def set_control(self, control_setting: ControlSetting):
        pass

    def get_control(self, control_setting_name: ValueName) -> ControlSetting:
        pass

    def start(self):
        pass

    def is_running(self) -> bool:
        pass

    def stop(self):
        pass

class CoordinatorLocal(CoordinatorBase):
    def __init__(self, sim_mode=False):
        """

        Args:
            sim_mode:

        Attributes:
            _is_running (:class:`threading.Event`): ``.set()`` when thread should stop

        """
        super().__init__(sim_mode=sim_mode)
        self.control_module = vent.controller.control_module.get_control_module(sim_mode)

    def get_sensors(self) -> Dict[ValueName, SensorValue]:
        sensor_values = self.control_module.get_sensors()
        res = {
            ValueName.PIP: SensorValue(ValueName.PIP, sensor_values.pip, sensor_values.timestamp,
                                       sensor_values.loop_counter),
            ValueName.PEEP: SensorValue(ValueName.PEEP, sensor_values.peep, sensor_values.timestamp,
                                        sensor_values.loop_counter),
            ValueName.FIO2: SensorValue(ValueName.FIO2, sensor_values.fio2, sensor_values.timestamp,
                                        sensor_values.loop_counter),
            ValueName.TEMP: SensorValue(ValueName.TEMP, sensor_values.temp, sensor_values.timestamp,
                                        sensor_values.loop_counter),
            ValueName.HUMIDITY: SensorValue(ValueName.HUMIDITY, sensor_values.humidity, sensor_values.timestamp,
                                            sensor_values.loop_counter),
            ValueName.PRESSURE: SensorValue(ValueName.PRESSURE, sensor_values.pressure, sensor_values.timestamp,
                                            sensor_values.loop_counter),
            ValueName.VTE: SensorValue(ValueName.VTE, sensor_values.vte, sensor_values.timestamp,
                                       sensor_values.loop_counter),
            ValueName.BREATHS_PER_MINUTE: SensorValue(ValueName.BREATHS_PER_MINUTE, sensor_values.breaths_per_minute,
                                                      sensor_values.timestamp, sensor_values.loop_counter),
            ValueName.INSPIRATION_TIME_SEC: SensorValue(ValueName.INSPIRATION_TIME_SEC,
                                                        sensor_values.inspiration_time_sec, sensor_values.timestamp,
                                                        sensor_values.loop_counter),
        }
        return res

    def get_active_alarms(self) -> Dict[str, Alarm]:
        return self.control_module.get_active_alarms()

    def get_logged_alarms(self) -> List[Alarm]:
        return self.control_module.get_logged_alarms()

    def clear_logged_alarms(self):
        # TODO: implement this
        raise NotImplementedError

    def set_control(self, control_setting: ControlSetting):
        self.control_module.set_control(control_setting)

    def get_control(self, control_setting_name: ValueName) -> ControlSetting:
        return self.control_module.get_control(control_setting_name)

    def start(self):
        """
        Start the coordinator.
        This does a soft start (not allocating a process).
        """
        self.control_module.start()

    def is_running(self) -> bool:
        """
        Test whether the whole system is running
        """
        return self.control_module._running

    def stop(self):
        """
        Stop the coordinator.
        This does a soft stop (not kill a process)
        """
        self.control_module.stop()


class CoordinatorRemote(CoordinatorBase):
    def __init__(self, sim_mode=False):
        super().__init__(sim_mode=sim_mode)
        # TODO: according to documentation, pass max_heartbeat_interval?
        self.process_manager = ProcessManager(sim_mode)
        self.proxy = get_rpc_client()
        # TODO: make sure the ipc connection is setup. There should be a clever method

    def get_sensors(self) -> Dict[ValueName, SensorValue]:
        sensor_values = pickle.loads(self.proxy.get_sensors().data)
        res = {
            ValueName.PIP: SensorValue(ValueName.PIP, sensor_values.pip, sensor_values.timestamp,
                                       sensor_values.loop_counter),
            ValueName.PEEP: SensorValue(ValueName.PEEP, sensor_values.peep, sensor_values.timestamp,
                                        sensor_values.loop_counter),
            ValueName.FIO2: SensorValue(ValueName.FIO2, sensor_values.fio2, sensor_values.timestamp,
                                        sensor_values.loop_counter),
            ValueName.TEMP: SensorValue(ValueName.TEMP, sensor_values.temp, sensor_values.timestamp,
                                        sensor_values.loop_counter),
            ValueName.HUMIDITY: SensorValue(ValueName.HUMIDITY, sensor_values.humidity, sensor_values.timestamp,
                                            sensor_values.loop_counter),
            ValueName.PRESSURE: SensorValue(ValueName.PRESSURE, sensor_values.pressure, sensor_values.timestamp,
                                            sensor_values.loop_counter),
            ValueName.VTE: SensorValue(ValueName.VTE, sensor_values.vte, sensor_values.timestamp,
                                       sensor_values.loop_counter),
            ValueName.BREATHS_PER_MINUTE: SensorValue(ValueName.BREATHS_PER_MINUTE, sensor_values.breaths_per_minute,
                                                      sensor_values.timestamp, sensor_values.loop_counter),
            ValueName.INSPIRATION_TIME_SEC: SensorValue(ValueName.INSPIRATION_TIME_SEC,
                                                        sensor_values.inspiration_time_sec, sensor_values.timestamp,
                                                        sensor_values.loop_counter),
        }
        return res

    def get_active_alarms(self) -> Dict[str, Alarm]:
        return pickle.loads(self.proxy.get_active_alarms())

    def get_logged_alarms(self) -> List[Alarm]:
        return pickle.loads(self.proxy.get_logged_alarms())

    def clear_logged_alarms(self):
        # TODO: implement this
        raise NotImplementedError

    def set_control(self, control_setting: ControlSetting):
        pickled_args = pickle.dumps(control_setting)
        self.proxy.set_control(pickled_args)

    def get_control(self, control_setting_name: ValueName) -> ControlSetting:
        pickled_args = pickle.dumps(control_setting_name)
        pickled_res = self.proxy.get_control(pickled_args).data
        return pickle.loads(pickled_res)

    def start(self):
        """
        Start the coordinator.
        This does a soft start (not allocating a process).
        """
        self.proxy.start()

    def is_running(self) -> bool:
        """
        Test whether the whole system is running
        """
        return self.proxy.is_running()

    def stop(self):
        """
        Stop the coordinator.
        This does a soft stop (not kill a process)
        """
        self.proxy.stop()


def get_coordinator(single_process=False, sim_mode=False) -> CoordinatorBase:
    if single_process:
        return CoordinatorLocal(sim_mode)
    else:
        return CoordinatorRemote(sim_mode)
