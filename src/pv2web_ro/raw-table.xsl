<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:template match="/">
        <html>
            <head>
                <title>pv2web_ro: EPICS process variables</title>
            </head>
            <body>
                <h1>pv2web_ro: raw PV data from EPICS</h1>
                <p>written by: <xsl:value-of select="/pv2web_ro/written_by"/></p>
                <p>date/time stamp: <xsl:value-of select="/pv2web_ro/datetime"/></p>

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
                    <xsl:apply-templates select="pv2web_ro/pv"/>
                </table>

                <hr />
                <p>
                    <small>
                        data gathered by: <xsl:value-of select="/pv2web_ro/writer"/>
                    </small>
                </p>
                <p>
                    <small>
                        report page: $Id: raw-table.xsl 803 2013-04-20 05:19:52Z jemian $
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
