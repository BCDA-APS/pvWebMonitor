<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
	version="1.0"
	description="simple example XSLT to EPICS PV value">

    <xsl:template match="/">
    	<html>
    		<body>
				EPICS PV: <xsl:value-of select="//pv[@id='VDM_Stripe']/name"/><br />
				
				PV value: <xsl:value-of select="//pv[@id='VDM_Stripe']/value"/><br />
				
				PV last updated: <xsl:value-of select="//pv[@id='VDM_Stripe']/timestamp"/><br />
				
				HTML file written: <xsl:value-of select="/pvWebMonitor/datetime"/>
    		</body>
    	</html>
    </xsl:template>

</xsl:stylesheet>
