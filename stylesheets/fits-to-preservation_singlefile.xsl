<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
    xmlns:premis="http://www.loc.gov/premis/v3"
    xmlns:dc="http://purl.org/dc/terms/"
    xpath-default-namespace="http://hul.harvard.edu/ois/xml/ns/fits/fits_output">
    <xsl:output method="xml" indent="yes" />
    
<!--Purpose: transform cleaned-up FITS output into the preservation.xml file when there is one file in the aip.-->
<!--For aips with more than one file, the fits-to-preservation_multifile.xsl stylesheet is used.-->

<!--The preservation.xml file is mostly PREMIS, with 2 Dublin Core fields, and is used for importing metadata into the ARCHive (digital preservation storage). See the UGA Libraries AIP Definition for details.-->
<!--FITS output is run through the fits-cleanup.xsl stylesheet before this stylesheet-->

<!--Ways that this stylesheet is different from fits-to-preservation_multifile:
    1. The optional filelist section is not included because it would be identical to the aip section, other than including the MD5 (which is also in the bag manifest)
    2. The premis:objectCategory in the aip section is file instead of representation
    3. The aip section includes if formats are valid or well formed
    4. The aip section includes creating application dates
    5. Templates in the aip section that match size, identity, valid, well-formed, tool, creatingApplication[string()], and inhibitor[inhibitorType] are the same as the equivalent templates in the filelist section of the multifile stylesheet.
    6. The multifile stylesheet has several additional templates, such as for md5 and file-id, which are not in this stylesheet-->


<!--..................................................................................................-->
<!--MAIN TEMPLATE: DOCUMENT STRUCTURE-->
<!--..................................................................................................-->

    <!--Creates the overall structure of the preservation.xml file-->
    <!--Inserts the values for aip title, rights, and aip objectCategory. -->
    <xsl:template match="/">
        <preservation>
            <dc:title><xsl:value-of select="$aip-title" /></dc:title>
            <dc:rights>http://rightsstatements.org/vocab/InC/1.0/</dc:rights>
            <aip>
                <premis:object>
                    <xsl:call-template name="aip-object-id" />
                    <xsl:call-template name="aip-version" />
                    <premis:objectCategory>file</premis:objectCategory>
                    <premis:objectCharacteristics>
                        <xsl:apply-templates select="combined-fits/fits/fileinfo/size" />
                        <xsl:apply-templates select="combined-fits/fits/identification/identity" />
                        <xsl:if test="$workflow='website'">
                            <xsl:call-template name="warc" />
                        </xsl:if>
                        <xsl:apply-templates select="combined-fits/fits/fileinfo/creatingApplication[string()]" />
                        <xsl:apply-templates select="combined-fits/fits/fileinfo/inhibitor[inhibitorType]" />
                    </premis:objectCharacteristics>
                    <xsl:call-template name="relationship-collection" />
                </premis:object>
            </aip>
        </preservation>
    </xsl:template>


<!--..................................................................................................-->
<!--PARAMETER, VARIABLES, and REGEX-->
<!--..................................................................................................-->

    <!--The aip id, aip title, and department are given as arguments when running the xslt via the command line or script.-->
    <!--The workflow type is an optional fourth argument used to run additional code for websites-->
    <xsl:param name="aip-id" required="yes" />
    <xsl:param name="aip-title" required="yes" />
    <xsl:param name="department" required="yes" />
    <xsl:param name="workflow" />

    <!--$uri: the unique identifier for the group in the ARCHive (digital preservation system).-->
    <xsl:variable name="uri">INSERT-URI/<xsl:value-of select="$department" /></xsl:variable>
        
    <!--$collection-id: gets the collection-id from the aip id.-->
    <!--Uses department parameter to determine what pattern to match.-->
    <xsl:variable name="collection-id">
 
       <!--Russell collection-id is formatted rbrl-###-->
        <xsl:if test="$department='russell'">
            <xsl:analyze-string select="$aip-id" regex="^(rbrl-\d{{3}})">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)" />
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:if>

        <!--Hargrett collection-id is formatted harg-ms####, harg-ua####, harg-ua##-####, or harg-0000-->
        <xsl:if test="$department='hargrett'">
            <xsl:analyze-string select="$aip-id" regex="^(harg-(ms|ua)?(\d{{2}}-)?\d{{4}})">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)" />
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:if>

        <!--Partner collection-id is formatted ####-->
        <xsl:if test="$department='emory'">
            <xsl:analyze-string select="$aip-id" regex="^(\d{{4}})_\d{{3}}">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)" />
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:if>

    </xsl:variable>


<!--..................................................................................................-->
<!--AIP SECTION TEMPLATES-->

<!--Detailed information about the file in the aip. When tools generate conflicting information (i.e. 
multiple possible formats or multiple possible created dates) all possible information is kept.-->
<!--..................................................................................................-->

    <!--aip id: PREMIS 1.1 (required): type is group uri and value is aip id from variables. -->
    <xsl:template name="aip-object-id">
        <premis:objectIdentifier>
            <premis:objectIdentifierType><xsl:value-of select="$uri" /></premis:objectIdentifierType>
            <premis:objectIdentifierValue><xsl:value-of select="$aip-id" /></premis:objectIdentifierValue>
        </premis:objectIdentifier>
    </xsl:template>
    
    
    <!--aip version: PREMIS 1.1 (required): type is aip uri and value is default version of 1.-->
    <xsl:template name="aip-version">
        <premis:objectIdentifier>
            <premis:objectIdentifierType>
                <xsl:value-of select="$uri" />/<xsl:value-of select="$aip-id" />
            </premis:objectIdentifierType>
            <premis:objectIdentifierValue>1</premis:objectIdentifierValue>
        </premis:objectIdentifier>
    </xsl:template>
    
    
    <!--aip size: PREMIS 1.5.3 (optional): gets file size in bytes.-->
    <xsl:template match="size">
        <premis:size><xsl:value-of select="." /></premis:size>
    </xsl:template>
    
    
    <!--file format list: PREMIS 1.5.4 (required)-->
    <!--If different tools get different results, makes an element for each name/version variation.-->
    <xsl:template match="identity">

        <premis:format>

            <!--Format name, and version if it has one.-->
            <premis:formatDesignation>
                <premis:formatName><xsl:value-of select="@format" /></premis:formatName>
                <xsl:if test="version">
                    <premis:formatVersion><xsl:value-of select="version" /></premis:formatVersion>
                </xsl:if>
            </premis:formatDesignation>

            <!--Format PUID, if it has one.-->
            <xsl:if test="externalIdentifier[@type = 'puid']">
                <premis:formatRegistry>
                    <premis:formatRegistryName>
                        <xsl:text>https://www.nationalarchives.gov.uk/PRONOM</xsl:text>
                    </premis:formatRegistryName>
                    <premis:formatRegistryKey>
                        <xsl:value-of select="externalIdentifier[@type = 'puid']" />
                    </premis:formatRegistryKey>
                    <premis:formatRegistryRole>specification</premis:formatRegistryRole>
                </premis:formatRegistry>
            </xsl:if>

            <!--Makes an invalid element to catch a new identifier type during validation.-->
            <xsl:if test="externalIdentifier[not(@type='puid')]">
                <premis:formatRegistry/>
            </xsl:if>

            <!--Makes the three kinds of format notes, all of which can repeat-->
            <!--If there are multiple format identifications, valid and well-formed notes are associated with the format identified by the same tool that determined a format was valid or well-formed.--> 
            <xsl:variable name="tool" select="tool/@toolname"/>
            <xsl:apply-templates select="../following-sibling::filestatus/valid[@toolname=$tool]" />
            <xsl:apply-templates select="../following-sibling::filestatus/well-formed[@toolname=$tool]" />
            <xsl:apply-templates select="tool" />

            <!--Makes an invalid element to catch missing required information during validation.-->
            <xsl:if test="not(tool)"><premis:formatNote /></xsl:if>

        </premis:format>
    </xsl:template>


    <!--For websites, adds warc identification because FITs is only identifying as gzip. -->
    <xsl:template name="warc">
        <premis:format>
            <premis:formatDesignation>
                <premis:formatName>WARC</premis:formatName>
            </premis:formatDesignation>
            <premis:formatRegistry>
                <premis:formatRegistryName>https://www.nationalarchives.gov.uk/PRONOM</premis:formatRegistryName>
                <premis:formatRegistryKey>fmt/289</premis:formatRegistryKey>
                    <premis:formatRegistryRole>specification</premis:formatRegistryRole>
            </premis:formatRegistry>
            <premis:formatNote>File was downloaded from Archive-It.org. According to their policies, it is a WARC.</premis:formatNote>
        </premis:format>
    </xsl:template>


    <!--Makes the valid format note. Used in the file format list.-->
    <xsl:template match="valid">
        <xsl:variable name="valid" select="." />
        <xsl:choose>
            <xsl:when test="$valid='true'">
                <premis:formatNote>
                    <xsl:text>Format identified as valid by </xsl:text>
                    <xsl:value-of select="$valid/@toolname" />
                    <xsl:text> version </xsl:text>
                    <xsl:value-of select="$valid/@toolversion" />
                </premis:formatNote>
            </xsl:when>
            <xsl:when test="$valid='false'">
                <premis:formatNote>
                    <xsl:text>Format identified as not valid by </xsl:text>
                    <xsl:value-of select="$valid/@toolname" />
                    <xsl:text> version </xsl:text>
                    <xsl:value-of select="$valid/@toolversion" />
                </premis:formatNote>
            </xsl:when>
            <!--Makes an invalid element to catch malformed information during validation.-->
            <xsl:otherwise><premis:formatNote /></xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    

    <!--Makes the well-formed format note. Used in the file format list.-->
    <xsl:template match="well-formed">
        <xsl:variable name="well-formed" select="." />
        <xsl:choose>
            <xsl:when test="$well-formed='true'">
                <premis:formatNote>
                    <xsl:text>Format identified as well-formed by </xsl:text>
                    <xsl:value-of select="$well-formed/@toolname" />
                    <xsl:text> version </xsl:text>
                    <xsl:value-of select="$well-formed/@toolversion" />
                </premis:formatNote>
            </xsl:when>
            <xsl:when test="$well-formed='false'">
                <premis:formatNote>
                    <xsl:text>Format identified as not well-formed by </xsl:text>
                    <xsl:value-of select="$well-formed/@toolname" />
                    <xsl:text> version </xsl:text>
                    <xsl:value-of select="$well-formed/@toolversion" />
                </premis:formatNote>
            </xsl:when>
            <!--Makes an invalid element to catch malformed information during validation.-->
            <xsl:otherwise><premis:formatNote /></xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    
    <!--Makes the format tool note. Used in the file format list.-->
    <xsl:template match="tool">
        <premis:formatNote>
            <xsl:text>Format identified by </xsl:text>
            <xsl:value-of select="@toolname" />
            <xsl:text> version </xsl:text>
            <xsl:value-of select="@toolversion" />
        </premis:formatNote>
    </xsl:template>
    
    
    <!--file creating applications: PREMIS 1.5.5 (optional)-->
    <!--If different tools get different results, makes an element for tool's results.-->
    <!--Does not make element if creatingApplication is empty (has no string()).-->
    <!--Known issue: date will be repeated if multiple tools agree on YYYY-MM-DD but not the time.-->
    <xsl:template match="creatingApplication[string()]">
        <premis:creatingApplication>

            <!--Application name, if any.-->
            <xsl:if test="creatingApplicationName">
                <premis:creatingApplicationName>
                <xsl:value-of select="creatingApplicationName" />
                </premis:creatingApplicationName>
            </xsl:if>

            <!--Application version, if any.-->
            <xsl:if test="creatingApplicationVersion">
                <premis:creatingApplicationVersion>
                    <xsl:value-of select="creatingApplicationVersion" />
                </premis:creatingApplicationVersion>
            </xsl:if>

            <!--Application date, if any, formatted YYYY-MM-DD.-->
            <!--Own template because of the amount of code required to get to the right format.-->
            <xsl:apply-templates select="created" />

        </premis:creatingApplication>
    </xsl:template>
    
    
    <!--file inhibitors: PREMIS 1.5.6 (required if applicable)-->
    <!--Only makes the element if there is an inhibitor type.-->
    <!--If different tools get different results, makes an element for tool's results.-->
    <xsl:template match="inhibitor[inhibitorType]">
        <premis:inhibitors>
            <premis:inhibitorType>
                <xsl:value-of select="inhibitorType" />
            </premis:inhibitorType>
            <xsl:if test="inhibitorTarget">
                <premis:inhibitorTarget>
                    <xsl:value-of select="inhibitorTarget" />
                </premis:inhibitorTarget>
            </xsl:if>
        </premis:inhibitors>
    </xsl:template>
    
    <!--Does not include target if there is not type because that is not valid PREMIS.-->
    <xsl:template match="inhibitorTarget" />
    
    
    <!--aip relationship to collection: PREMIS 1.13 (required if applicable)-->
    <xsl:template name="relationship-collection">
        <!--Does not include the default number for web archives aips without a related collection.-->
        <xsl:if test="not($collection-id='harg-0000' or $collection-id='rbrl-000')">
            <premis:relationship>
                <premis:relationshipType>structural</premis:relationshipType>
                <premis:relationshipSubType>Is Member Of</premis:relationshipSubType>
                <premis:relatedObjectIdentifier>
                    <premis:relatedObjectIdentifierType>
                        <xsl:value-of select="$uri" />
                    </premis:relatedObjectIdentifierType>
                    <premis:relatedObjectIdentifierValue>
                        <xsl:value-of select="$collection-id" />
                    </premis:relatedObjectIdentifierValue>
                </premis:relatedObjectIdentifier>
            </premis:relationship>
        </xsl:if>
    </xsl:template>
    

<!--..................................................................................................-->
<!--CREATED DATE REFORMATTING TEMPLATE-->

<!--This template tests for each known date format and reformats it to the required YYYY-MM-DD by using regular expressions to extract the day, month, and year information and then reconfiguring them to the correct order and number of digits.-->

<!--If a new date format is encountered, the "otherwise" option will create an invalid premis:dateCreatedByApplication element so that the preservation.xml causes a validation error so staff know to update this stylesheet.-->
<!--..................................................................................................-->

    <xsl:template match="created">
        <xsl:variable name="apdate" select="." />
        <xsl:choose>
        
            <!--Does not include a date element if value is 0.-->
            <xsl:when test="$apdate='0'" />
            <xsl:when test="$apdate='0000:00:00 00:00:00'" />
            <xsl:when test="matches($apdate, '0-00-00T')" />

            <!--Pattern: Year:Month:Day Time and Year-Month-Day Time-->
            <!--Examples: 2018:01:02 01:02:33; 2000-10-05 9:15 PM-->
            <xsl:when test="matches($apdate, '^\d{4}(:|-)\d{2}(:|-)\d{2} ')">
                <premis:dateCreatedByApplication>
                    <!--Gets content before the space (removes time portion).-->
                    <xsl:variable name="dateString">
                        <xsl:value-of select="substring-before($apdate, ' ')" />
                    </xsl:variable>
                    <!--Replaces any colon with a dash.-->
                    <xsl:value-of select="replace($dateString, ':', '-')" />
                </premis:dateCreatedByApplication>
            </xsl:when>
            
            <!--Pattern: Day.Month.Year(,) Time with all numbers-->
            <!--Examples: 23.07.98, 2:28 AM; 18.9.98, 12:50 PM; 2.9.98 11:42 PM-->
            <xsl:when test="matches($apdate, '(\d{1,2})\.(\d{1,2})\.(\d{2}),? \d{1,2}:\d{1,2} (AM|PM)')">
                <premis:dateCreatedByApplication>
                    <!--Gets the day, month, and year as separate regex groups.-->
                    <xsl:analyze-string select="$apdate" regex="(\d{{1,2}})\.(\d{{1,2}})\.(\d{{2}}),? \d{{1,2}}:\d{{1,2}} (AM|PM)">
                    
                        <!--Reformats each date component and recombines to make YYYY-MM-DD format.-->
                        <xsl:matching-substring>

                            <!--Year: makes four digits by adding '19' or '20'.-->
                            <xsl:variable name="year">
                                <xsl:choose>
                                    <!--If less than 50, assumes 21st century.-->
                                    <xsl:when test="number(regex-group(3)) &lt; 50">
                                        <xsl:text>20</xsl:text><xsl:value-of select="regex-group(3)" />
                                    </xsl:when>
                                    <!--If 50 or more, assumes 20th century.-->
                                    <xsl:otherwise>
                                        <xsl:text>19</xsl:text><xsl:value-of select="regex-group(3)" />
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>

                            <!--Month: adds leading zero if not already a two-digit number.-->
                            <xsl:variable name="month">
                                <xsl:value-of select="format-number(number(regex-group(2)),'00')" />
                            </xsl:variable>

                            <!--Day: adds leading zero if not already a two-digit number.-->
                            <xsl:variable name="day">
                                <xsl:value-of select="format-number(number(regex-group(1)),'00')" />
                            </xsl:variable>

                            <!--Combines the date components in the correct order-->
                            <xsl:value-of select="$year, $month, $day" separator="-" />

                        </xsl:matching-substring>
                    </xsl:analyze-string>
                </premis:dateCreatedByApplication>
            </xsl:when>

            <!--Pattern: Day Month Year Time with month spelled out-->
            <!--Example: 24 September 2002 11:26:49 AM -->
            <xsl:when test="matches($apdate, '\d{1,2} [a-zA-Z]+ \d{4} ')">
                <premis:dateCreatedByApplication>
                    <!--Gets the day, month, and year as separate regex groups. -->
                    <xsl:analyze-string select="$apdate" regex="(\d{{1,2}}) ([a-zA-Z]+) (\d{{4}}) ">
                        <!--Reformats each date component and recombines to make YYYY-MM-DD format. -->
                        <xsl:matching-substring>

                            <!--Year: already formatted correctly. -->
                            <xsl:variable name="year">
                                <xsl:value-of select="regex-group(3)" />
                            </xsl:variable>

                            <!--Month: converts from word or abbreviation to two-digit number. -->
                            <xsl:variable name="month">
                                <xsl:if test="matches(regex-group(2), '^Jan')">01</xsl:if>
                                <xsl:if test="matches(regex-group(2), '^Feb')">02</xsl:if>
                                <xsl:if test="matches(regex-group(2), '^Mar')">03</xsl:if>
                                <xsl:if test="matches(regex-group(2), '^Apr')">04</xsl:if>
                                <xsl:if test="matches(regex-group(2), '^May')">05</xsl:if>
                                <xsl:if test="matches(regex-group(2), '^Jun')">06</xsl:if>
                                <xsl:if test="matches(regex-group(2), '^Jul')">07</xsl:if>
                                <xsl:if test="matches(regex-group(2), '^Aug')">08</xsl:if>
                                <xsl:if test="matches(regex-group(2), '^Sep')">09</xsl:if>
                                <xsl:if test="matches(regex-group(2), '^Oct')">10</xsl:if>
                                <xsl:if test="matches(regex-group(2), '^Nov')">11</xsl:if>
                                <xsl:if test="matches(regex-group(2), '^Dec')">12</xsl:if>
                            </xsl:variable>

                            <!--Day: adds leading zero if not already a two-digit number. -->
                            <xsl:variable name="day">
                                <xsl:value-of select="format-number(number(regex-group(1)),'00')" />
                            </xsl:variable>

                            <!--Combines the date components in the correct order -->
                            <xsl:value-of select="$year, $month, $day" separator="-" />

                        </xsl:matching-substring>
                    </xsl:analyze-string>
                </premis:dateCreatedByApplication>
            </xsl:when>

            <!--Pattern: Month/Day/Year Time with all numbers-->
            <!--Examples: 12/01/99 12:01 PM; 1/5/2011 1:11:55--> 
            <xsl:when test="matches($apdate, '\d{1,2}/\d{1,2}/\d{2,4}')">
                <premis:dateCreatedByApplication>
                    <!--Gets the day, month, and year as separate regex groups.-->
                    <xsl:analyze-string select="$apdate" regex="(\d{{1,2}})/(\d{{1,2}})/(\d{{2,4}})">

                        <!--Reformats each date component and recombines to make YYYY-MM-DD format.-->
                        <xsl:matching-substring>

                            <!--Year: makes four digits by adding '19' or '20'.-->
                            <xsl:variable name="year">
                                <xsl:choose>
                                    <!--Already a four digit year. Leave as is.-->
                                    <xsl:when test="number(regex-group(3)) &gt; 999">
                                        <xsl:value-of select="regex-group(3)" />
                                    </xsl:when>
                                    <!--If less than 50, assumes 21st century.-->
                                    <xsl:when test="number(regex-group(3)) &lt; 50">
                                        <xsl:text>20</xsl:text><xsl:value-of select="regex-group(3)" />
                                    </xsl:when>
                                    <!--If 50 or more, assumes 20th century.-->
                                    <xsl:otherwise>
                                        <xsl:text>19</xsl:text><xsl:value-of select="regex-group(3)" />
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>

                            <!--Month: adds leading zero if not already a two-digit number.-->
                            <xsl:variable name="month">
                                <xsl:value-of select="format-number(number(regex-group(1)),'00')" />
                            </xsl:variable>

                            <!--Day: adds leading zero if not already a two-digit number.-->
                            <xsl:variable name="day">
                                <xsl:value-of select="format-number(number(regex-group(2)),'00')" />
                            </xsl:variable>

                            <!--Combines the date components in the correct order-->
                            <xsl:value-of select="$year, $month, $day" separator="-" />

                        </xsl:matching-substring>
                    </xsl:analyze-string>
                </premis:dateCreatedByApplication>
            </xsl:when>

            <!--Pattern: (Day of Week) Month ( )Day(,) (Time) Year with month spelled out-->
            <!--Content in the parenthesis may or may not be present.-->
            <!--Examples: May 5, 2004; Monday, January 7, 2001 11:22:33 PM; 
                          Wed Mar 01 11:22:33 EST 2003; Thu Apr  2 20:05:01 1998 -->
            <xsl:when test="matches($apdate, '[a-zA-Z]+  ?\d{1,2},? [0-9:A-Z ]*\d{4}')">
                <premis:dateCreatedByApplication>
                    <!--Gets the day, month, and year as separate regex groups.-->
                    <xsl:analyze-string select="$apdate" regex="([a-zA-Z]+)  ?(\d{{1,2}}),? [0-9:A-Z ]*(\d{{4}})">
                        <!--Reformats each date component and recombines to make YYYY-MM-DD format.-->
                        <xsl:matching-substring>

                            <!--Year: already formatted correctly.-->
                            <xsl:variable name="year">
                                <xsl:value-of select="regex-group(3)" />
                            </xsl:variable>

                            <!--Month: converts from word or abbreviation to two-digit number.-->
                            <xsl:variable name="month">
                                <xsl:if test="matches(regex-group(1), '^Jan')">01</xsl:if>
                                <xsl:if test="matches(regex-group(1), '^Feb')">02</xsl:if>
                                <xsl:if test="matches(regex-group(1), '^Mar')">03</xsl:if>
                                <xsl:if test="matches(regex-group(1), '^Apr')">04</xsl:if>
                                <xsl:if test="matches(regex-group(1), '^May')">05</xsl:if>
                                <xsl:if test="matches(regex-group(1), '^Jun')">06</xsl:if>
                                <xsl:if test="matches(regex-group(1), '^Jul')">07</xsl:if>
                                <xsl:if test="matches(regex-group(1), '^Aug')">08</xsl:if>
                                <xsl:if test="matches(regex-group(1), '^Sep')">09</xsl:if>
                                <xsl:if test="matches(regex-group(1), '^Oct')">10</xsl:if>
                                <xsl:if test="matches(regex-group(1), '^Nov')">11</xsl:if>
                                <xsl:if test="matches(regex-group(1), '^Dec')">12</xsl:if>
                            </xsl:variable>

                            <!--Day: adds leading zero if not already a two-digit number.-->
                            <xsl:variable name="day">
                                <xsl:value-of select="format-number(number(regex-group(2)),'00')" />
                            </xsl:variable>

                            <!--Combines the date components in the correct order-->
                            <xsl:value-of select="$year, $month, $day" separator="-" />

                        </xsl:matching-substring>
                    </xsl:analyze-string>
                </premis:dateCreatedByApplication>
            </xsl:when>
            
            <!--Makes an invalid element to catch new date formats during validation.-->
            <xsl:otherwise>
                <premis:dateCreatedByApplication>
                    <xsl:text>New Date Format Identified: Update Stylesheet</xsl:text>
                </premis:dateCreatedByApplication>
            </xsl:otherwise>
            
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>

