<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
    xpath-default-namespace="http://hul.harvard.edu/ois/xml/ns/fits/fits_output">
    <xsl:output method="xml" indent="yes" />
    <xsl:strip-space elements="*" />
    
<!--Purpose: simplify FITS output to make it easier to make the preservation.xml file:-->
<!--    *Removes empty elements and sections that are not used.
        *Makes the order of children elements consistent.
        *Creates one FITS identity section for each version of a format
        *Adds structure to the creating application and inhibitor information-->

<!--Copies elements without their namespaces so namespaces are not added as element attribute.-->
<!--All elements are still within the FITS namespace.-->

    
    <!--Maintains the overall document structure. Copies directly if doesn't match another template.-->
    <xsl:template match="node()|@*">
        <xsl:copy><xsl:apply-templates select="node()|@*" /></xsl:copy>
    </xsl:template>

    
    <!--Creates identity element and makes the order of the children elements consistent-->
    <!--If there are versions, makes one identity element per version-->
    <!--Known issue: if no identity elements have an @format value, get an empty identification element.-->
    <xsl:template match="identification/identity">
        <!--Will not make an identity element if the format does not have a name.-->
        <xsl:if test="@format !=''">
            <xsl:choose>

                <!--If at least one identity has a version, reorganizes into one identity per version.-->
                <xsl:when test="version[string()]">
                    <xsl:apply-templates select="version[string()]" />
                </xsl:when>

                <!--Reorganizes the identity element if no identity has a version.-->
                <xsl:otherwise>
                    <identity format="{@format}" xmlns="http://hul.harvard.edu/ois/xml/ns/fits/fits_output">           <!--Identifying tool, if not empty-->
                        <xsl:copy-of select="tool[not(@toolname='')]" copy-namespaces="no" />
                        <!--All PUIDs, if not empty.-->
                        <xsl:if test="externalIdentifier[@type='puid'][string()]">
                            <externalIdentifier type="puid">
                                <xsl:value-of select="externalIdentifier[@type='puid'][string()]" />
                            </externalIdentifier>
                        </xsl:if>
                        <!--All identifiers that are not PUIDs, if not empty.-->
                        <xsl:if test="externalIdentifier[not(@type='puid')][string()]">
                            <xsl:copy-of select="externalIdentifier[not(@type='puid')][string()]" />
                        </xsl:if>
                    </identity>
                </xsl:otherwise>

            </xsl:choose>
        </xsl:if>
    </xsl:template>


    <!--Makes one identity element per version and copies the other format information into each one.-->
    <xsl:template match="version[string()]">
        <identity format="{../@format}" xmlns="http://hul.harvard.edu/ois/xml/ns/fits/fits_output">
            <!--Identifying tool, if not empty.-->
            <xsl:copy-of select="../tool[not(@toolname='')]" copy-namespaces="no" />
            <!--Format version.-->
            <xsl:copy-of select="." copy-namespaces="no" />
            <!--All PUIDs, if not empty.-->
            <xsl:if test="../externalIdentifier[@type='puid'][string()]">
                <externalIdentifier type="puid">
                    <xsl:value-of select="../externalIdentifier[@type='puid'][string()]" />
                </externalIdentifier>
            </xsl:if>
            <!--All identifiers that are not PUIDs, if not empty.-->
            <xsl:if test="externalIdentifier[not(@type='puid')][string()]">
                <xsl:copy-of select="externalIdentifier[not(@type='puid')][string()]" />
            </xsl:if>
        </identity>
    </xsl:template>


    <!--Adds structure to fileinfo with new elements creatingApplication and inhibitor.-->
    <!--New elements are given the FITs namespace for easier XPaths when make preservation.xml-->
    <!--Also makes the order of the child elements consistent.-->
    <xsl:template match="fileinfo">
        <fileinfo xmlns="http://hul.harvard.edu/ois/xml/ns/fits/fits_output">
            <xsl:apply-templates select="filepath" />
            <xsl:apply-templates select="size" />
            <xsl:apply-templates select="md5checksum" />

            <!--Makes a new element, creatingApplication, for each tool.-->
            <!--Children are date (created), name, and version elements, in that order.-->
            <!--Only copies a child element if it is not empty and not equal to 0.-->
            <!--Known issue: if all elements for a tool are empty, get an empty creatingApplication.-->
            <xsl:for-each-group select="created | creatingApplicationName | creatingApplicationVersion" group-by="@toolname">
                <creatingApplication tool="{@toolname}" xmlns="http://hul.harvard.edu/ois/xml/ns/fits/fits_output">
                    <xsl:for-each select="current-group()">
                        <xsl:sort select="name()" />
                        <xsl:if test=".[string()] and not(.='0')">
                            <xsl:copy-of select="." copy-namespaces="no" />
                        </xsl:if>
                    </xsl:for-each>
                </creatingApplication>
            </xsl:for-each-group>

            <!--Makes a new element, inhibitor, for each tool.-->
            <!--Children are inhibitorType and inhibitorTarget, listed in that order.-->
            <!--Only copies a child lement if it is not empty.-->
            <!--Known issue: if both elements for a tool are empty, get an empty inhibitor element.-->
            <xsl:for-each-group select="inhibitorType | inhibitorTarget" group-by="@toolname">
                <inhibitor tool="{@toolname}" xmlns="http://hul.harvard.edu/ois/xml/ns/fits/fits_output">
                    <xsl:for-each select="current-group()">
                        <xsl:sort select="name()" order="descending" />
                        <xsl:if test=".[string()]">
                            <xsl:copy-of select="." copy-namespaces="no" />
                        </xsl:if>
                    </xsl:for-each>
                </inhibitor>
            </xsl:for-each-group>
        </fileinfo>
    </xsl:template>

    
    <!--Only copies the filestatus element if it has valid and/or well-formed children with a value.-->    
    <!--Makes the order of child elements consistent.-->
    <xsl:template match="filestatus">
        <xsl:if test="valid[string()] or well-formed[string()]">
            <filestatus xmlns="http://hul.harvard.edu/ois/xml/ns/fits/fits_output">
                <xsl:apply-templates select="valid" />
                <xsl:apply-templates select="well-formed" />
            </filestatus>
        </xsl:if>
    </xsl:template>

    
    <!--Does not copy these two elements or their children-->
    <xsl:template match="metadata | statistics" />

    
    <!--Only copies these elements when apply-templates if they have a value.-->
    <xsl:template match="version | size | md5checksum | valid | well-formed">
        <xsl:if test=".[string()]"><xsl:copy-of select="." copy-namespaces="no" /></xsl:if>
    </xsl:template>
    
    <!--Only copies filepath when apply-templates if it has a value.-->
	<!--Replaces \ with / so any paths made by Windows match paths made by Linux (most common environment) for consistent file ids-->
    <xsl:template match="filepath">
    	<xsl:if test=".[string()]">
    		<filepath xmlns="http://hul.harvard.edu/ois/xml/ns/fits/fits_output"><xsl:copy-of select="replace(.,'\\','/')" copy-namespaces="no" /></filepath>
    	</xsl:if>
    </xsl:template>

</xsl:stylesheet>
