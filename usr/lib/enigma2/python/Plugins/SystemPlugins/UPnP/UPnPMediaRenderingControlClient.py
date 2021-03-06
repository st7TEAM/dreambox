class UPnPMediaRenderingControlClient(object):
	STATE_STOPPED = "STOPPED"
	STATE_PAUSED_PLAYBACK = "PAUSED_PLAYBACK"
	STATE_PLAYING = "PLAYING"
	STATE_TRANSITIONING = "TRANSITIONING"
	STATE_NO_MEDIA_PRESENT = "NO_MEDIA_PRESENT"
	CONNECTION_STATE_ERROR = "ERROR"
	TRANSPORT_STATE_OK = "OK"

	UPNP_NOT_IMPLEMENTED = "NOT_IMPLEMENTED"

	def __init__(self, client):
		self.__client = client #MediaRendererClient
		self.__transport = self.__client.av_transport #AVTransportClient
		self.__renderclient = self.__client.rendering_control #RenderingControlClient
		#useless without avtransport- and/or renderering client
		assert self.__transport is not None
		assert self.__renderclient is not None

		self.onTransportStatusChanged = []
		self.onPlaybackStatusChanged = []
		self.onDurationChanged = []
		self.onPositionChanged = []

		self.__subscribe()

	def __subscribe(self):
		for var in ["TransportStatus", "TransportState", "CurrentTrackDuration", "AbsoluteTimePosition"]:
			self.__transport.subscribe_for_variable(var, self.__onStateVariableChanged, signal=True)

	def __onStateVariableChanged(self, variable):
		print "__onStateVariableChanged: %s=%s" %(variable.name, variable.value)
		if variable.name == "TransportStatus":
			self.__onTransportStatusChanged(variable.value)
		elif variable.name == "TransportState":
			self.__onTransportStateChanged(variable.value)
		elif variable.name == "CurrentTrackDuration":
			self.__onDurationChanged(variable.value)
		elif variable.name == "AbsoluteTimePosition":
			self.__onPositionChanged(variable.value)

	def __onTransportStatusChanged(self, status):
		print "__onTransportStatusChanged status=%s" %(status)
		for fnc in self.onTransportStatusChanged:
			fnc(status)

	def __onTransportStateChanged(self, state):
		print "__onTransportStateChanged state=%s" %(state)
		for fnc in self.onPlaybackStatusChanged:
			fnc(state)

	'''
	converts a upnp timestamp in the format HH:mm:ss to seconds
	e.g.: 00:01:30 -> 90
	'''
	def __tsToSecs(self, timestamp):
		val = timestamp.split(":")
		secs = (float(val[0]) * 3600) + (float(val[1]) * 60) + float(val[2])
		return secs

	def __onDurationChanged(self, duration):
		print "[UPnPMediaRenderingControlClient].__onDurationChanged, duration=%s" %duration
		for fnc in self.onDurationChanged:
			fnc( self.__tsToSecs(duration) )

	def __onPositionChanged(self, pos):
		print "[UPnPMediaRenderingControlClient].__onPositionChanged, pos=%s" %pos
		for fnc in self.onPositionChanged:
			fnc( self.__tsToSecs(pos) )

	def getDeviceName(self):
		return self.__client.device.get_friendly_name()

	def setMediaUri(self, uri = '', metadata = ''):
		self.__transport.set_av_transport_uri(current_uri=uri, current_uri_metadata=metadata)

	def setNextMediaUri(self, uri = '', metadata = ''):
		self.__transport.set_next_av_transport_uri(next_uri=uri, next_uri_metadata=metadata)

	def playUri(self, uri = '', metadata = ''):
		self.setMediaUri(uri, metadata)
		self.play()

	def getPosition(self):
		return self.__transport.get_position_info()

	def play(self):
		self.__transport.play()

	def pause(self):
		self.__transport.pause()

	def seek(self, target):
		self.__transport.seek(target=target)

	def next(self):
		self.__transport.next()

	def prev(self):
		self.__transport.previous()

	def stop(self):
		self.__transport.stop()

	def getMute(self):
		return self.__renderclient.get_mute() == 1

	def setMute(self, mute):
		val = int(mute)
		self.__renderclient.set_mute(desired_mute=val)

	def getVolume(self):
		return self.__renderclient.get_volume()

	def setVolume(self, target):
		self.__renderclient.set_volume(desired_volume=target)

