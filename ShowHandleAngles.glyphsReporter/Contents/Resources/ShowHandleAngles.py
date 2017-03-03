#!/usr/bin/env python
# encoding: utf-8
import objc
from Foundation import *
from AppKit import *
import sys, os, re
import math
from GlyphsApp import OFFCURVE, LINE

MainBundle = NSBundle.mainBundle()
path = MainBundle.bundlePath() + "/Contents/Scripts"
if not path in sys.path:
	sys.path.append( path )

EPSILON = 0.1

import GlyphsApp

GlyphsReporterProtocol = objc.protocolNamed( "GlyphsReporter" )

class ShowHandleAngles ( NSObject, GlyphsReporterProtocol ):
	
	def init( self ):
		return self

	def interfaceVersion( self ):
		return 1

	def title( self ):
		return "Handle Angles"

	def keyEquivalent( self ):
		return None

	def modifierMask( self ):
		return 0

	def drawForegroundForLayer_( self, Layer ):
		pass

	def straight(self,p1,p2):
		n = self.nAngle(p1,p2)
		if abs(n-90) <= EPSILON or abs(n+90) <= EPSILON:
			return True
		if abs(n) <= EPSILON or abs(n-180) <= EPSILON:
			return True
		return False

	def nAngle(self,p1,p2):
		rads = math.atan2(p2.y-p1.y, p2.x-p1.x)
		return math.degrees(rads)

	def drawHandleAngles( self, Layer ):
		for thisPath in Layer.paths:
			for node in thisPath.nodes:
				if (node.type != OFFCURVE and node.nextNode.type == OFFCURVE) or (node.type == LINE and node.nextNode.type == LINE):
					p1 = node.position
					p2 = node.nextNode.position
					if not self.straight(p1,p2):
						lerp = ((p1.x+p2.x)/2, (p1.y+p2.y)/2)
						self.drawTextAtPoint( u"%d°" % self.nAngle(p1,p2), lerp)
				if (node.type != OFFCURVE and node.prevNode.type == OFFCURVE):
					p1 = node.position
					p2 = node.prevNode.position
					if not self.straight(p1,p2):
						lerp = ((p1.x+p2.x)/2, (p1.y+p2.y)/2)
						self.drawTextAtPoint( u"%d°" % self.nAngle(p1,p2), lerp)

	def drawBackgroundForLayer_( self, Layer ):
		try:
			self.drawHandleAngles( Layer )
		except Exception as e:
			self.logToConsole( "drawBackgroundForLayer_: %s" % str(e) )

	def drawBackgroundForInactiveLayer_( self, Layer ):
		pass

	def drawTextAtPoint( self, text, textPosition, fontSize=10.0, fontColor=NSColor.colorWithCalibratedRed_green_blue_alpha_( 1, 0, .5, 1 ) ):
		"""
		Use self.drawTextAtPoint( "blabla", myNSPoint ) to display left-aligned text at myNSPoint.
		"""
		try:
			glyphEditView = self.controller.graphicView()
			currentZoom = self.getScale()
			fontAttributes = { 
				NSFontAttributeName: NSFont.labelFontOfSize_( fontSize/currentZoom ),
				NSForegroundColorAttributeName: fontColor }
			displayText = NSAttributedString.alloc().initWithString_attributes_( text, fontAttributes )
			textAlignment = 2 # top left: 6, top center: 7, top right: 8, center left: 3, center center: 4, center right: 5, bottom left: 0, bottom center: 1, bottom right: 2
			glyphEditView.drawText_atPoint_alignment_( displayText, textPosition, textAlignment )
		except Exception as e:
			self.logToConsole( "drawTextAtPoint: %s" % str(e) )
	
	def needsExtraMainOutlineDrawingForInactiveLayer_( self, Layer ):
		return True

	def getHandleSize( self ):
		"""
		Returns the current handle size as set in user preferences.
		Use: self.getHandleSize() / self.getScale()
		to determine the right size for drawing on the canvas.
		"""
		try:
			Selected = NSUserDefaults.standardUserDefaults().integerForKey_( "GSHandleSize" )
			if Selected == 0:
				return 5.0
			elif Selected == 2:
				return 10.0
			else:
				return 7.0 # Regular
		except Exception as e:
			self.logToConsole( "getHandleSize: HandleSize defaulting to 7.0. %s" % str(e) )
			return 7.0

	def getScale( self ):
		"""
		self.getScale() returns the current scale factor of the Edit View UI.
		Divide any scalable size by this value in order to keep the same apparent pixel size.
		"""
		try:
			return self.controller.graphicView().scale()
		except:
			self.logToConsole( "Scale defaulting to 1.0" )
			return 1.0
	
	def setController_( self, Controller ):
		"""
		Use self.controller as object for the current view controller.
		"""
		try:
			self.controller = Controller
		except Exception as e:
			self.logToConsole( "Could not set controller" )
	
	def logToConsole( self, message ):
		"""
		The variable 'message' will be passed to Console.app.
		Use self.logToConsole( "bla bla" ) for debugging.
		"""
		myLog = "Show %s plugin:\n%s" % ( self.title(), message )
		NSLog( myLog )
