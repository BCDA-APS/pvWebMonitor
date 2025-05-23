<?xml version="1.0" encoding="UTF-8"?>
<!-- 
# Copyright (c) 2002-2025, University of Chicago, The Regents of the University of California, and Berliner Elektronenspeicherring Gesellschaft fuer Synchrotronstrahlung m.b.H. (BESSY) All rights reserved.
# See LICENSE file for details.
 -->
<xsl:stylesheet 
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
	version="1.0"
	description="XSLT file to display the raw values of monitored EPICS PVs"
>

    <xsl:template match="/">
        <html>
            <head>
                <title>pvWebMonitor: EPICS process variables</title>
            </head>
            <body>
                <h1>pvWebMonitor: raw PV data from EPICS</h1>
                <p>written by: <xsl:value-of select="/pvWebMonitor/written_by"/></p>
                <p>date/time stamp: <xsl:value-of select="/pvWebMonitor/datetime"/></p>

                <hr />
                
                <h2> EPICS process variables </h2>
                <table border="2">
                    <tr style="background-color: grey; color: white;">
                        <th>name</th>
                        <th>id</th>
                        <th>description</th>
                        <th>value</th>
                        <th>units</th>
                        <th>timestamp</th>
                    </tr>
                    <xsl:apply-templates select="pvWebMonitor/pv"/>
                </table>

                <hr />
                <p>
                    <small>
                        data gathered by: <tt><xsl:value-of select="/pvWebMonitor/written_by"/></tt>
                    </small>
                </p>
                <p>
                    <small>
                        report page: <tt>raw-table.xsl</tt>
                    </small>
                </p>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="pv">
        <tr>
 	    <xsl:if test="position() mod 2=0">
 	      <xsl:attribute name="bgcolor">Azure</xsl:attribute>
 	    </xsl:if>
            <td><xsl:value-of select="name"/></td>
            <td><xsl:value-of select="id"/></td>
            <td><xsl:value-of select="description"/></td>
            <td><xsl:value-of select="value"/></td>
            <td><xsl:value-of select="units"/></td>
            <td><xsl:value-of select="timestamp"/></td>
        </tr>
    </xsl:template>

    <xsl:template match="scan">
        <tr>
            <xsl:if test="position() mod 2=0">
              <xsl:attribute name="bgcolor">Azure</xsl:attribute>
            </xsl:if>
            <td><xsl:value-of select="title"/></td>
            <td><xsl:value-of select="@key"/></td>
            <td><xsl:value-of select="@specfile"/></td>
        </tr>
    </xsl:template>

</xsl:stylesheet>
