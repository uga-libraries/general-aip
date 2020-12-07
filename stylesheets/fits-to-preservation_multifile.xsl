<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"
    xmlns:premis="http://www.loc.gov/premis/v3"
    xmlns:dc="http://purl.org/dc/terms/"
    xpath-default-namespace="http://hul.harvard.edu/ois/xml/ns/fits/fits_output">
    <xsl:output method="xml" indent="yes" />
     <xsl:strip-space elements="*" />
    
<!--Purpose: transform cleaned-up FITS output into the preservation.xml file when there is more than one file in the aip. For aips with one file, the fits-to-preservation_singlefile.xsl stylesheet is used.-->
<!--The preservation.xml file is mostly PREMIS, with 2 Dublin Core fields, and is used for importing metadata into the ARCHive (digital preservation storage). See the UGA Libraries AIP Definition for details.-->
<!--FITS output is run through the fits-cleanup.xsl stylesheet before it is run through this stylesheet-->


<!--..................................................................................................-->
<!--MAIN TEMPLATE: DOCUMENT STRUCTURE -->
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
                    <premis:objectCategory>representation</premis:objectCategory>
                    <premis:objectCharacteristics>
                        <xsl:call-template name="aip-size" />
                        <xsl:call-template name="aip-unique-formats-list" />
                        <xsl:if test="$workflow='website'">
                            <xsl:call-template name="warc" />
                        </xsl:if>
                        <xsl:call-template name="aip-unique-creating-application-list" />
                        <xsl:call-template name="aip-unique-inhibitors-list" />
                    </premis:objectCharacteristics>
                    <xsl:call-template name="relationship-collection" />
                </premis:object>
            </aip>
            <filelist>
                <xsl:apply-templates select="combined-fits/fits" />
            </filelist>
        </preservation>
    </xsl:template>
    
    
<!--..................................................................................................-->
<!--PARAMETER, VARIABLES, and REGEX-->
<!--..................................................................................................-->
    
    <!--The aip id, aip title, and department are given as arguments when running the xslt via the command line or script.-->
    <!--The workflow type is an optional fourth argument used to run additional code for websites-->
    <!--PARTNER: CONFIRMED THAT GETTING EXPECTED AIP-ID AND DEPARTMENT PARAMETERS-->
    <xsl:param name="aip-id" required="yes" />
    <xsl:param name="aip-title" required="yes" />
    <xsl:param name="department" required="yes" />
    <xsl:param name="workflow" />
    
    <!--$uri: the unique identifier for the group in the ARCHive (digital preservation system).-->
    <!--PARTNER: THIS WORKS CORRECTLY-->
    <xsl:variable name="uri">INSERT-URI<xsl:value-of select="$department" /></xsl:variable>
         
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
        <!--TODO: THIS PRODUCES A BLANK FOR PARTNER-->
        <xsl:if test="$department='partner'">
            <xsl:analyze-string select="$aip-id" regex="^(\d{{4}})_\d{{3}}">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)" />
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:if>

    </xsl:variable>
    
    <!--file-id: the portion of the file path beginning with the aip id.-->
    <!--Gets the file id from each instance of fits/fileinfo/filepath-->
    <!--Uses department parameter to determine what pattern to match.-->
    <xsl:template name="get-file-id">
        <xsl:if test="$department='russell'">
            <xsl:analyze-string select="fileinfo/filepath" regex="rbrl-\d{{3}}-(er|web)-\d{{6}}(-\d{{4}})?.*">
                <xsl:matching-substring>
                    <xsl:value-of select="." />
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:if>
        <xsl:if test="$department='hargrett'">
            <xsl:analyze-string select="fileinfo/filepath" regex="harg-(ms|ua)?(\d{{2}}-)?\d{{4}}(er|-web-\d{{6}}-)\d{{4}}.*">
                <xsl:matching-substring>
                    <xsl:value-of select="." />
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:if>
        <!--TODO: THIS PRODUCES A BLANK FOR PARTNER-->
        <xsl:if test="$department='partner'">
            <xsl:analyze-string select="fileinfo/filepath" regex="\d{{4}}_\d{{3}}.*">
                <xsl:matching-substring>
                    <xsl:value-of select="." />
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:if>
    </xsl:template>
    
    
<!--.................................................................................................-->
<!--AIP SECTION TEMPLATES -->

<!--Summary information about the AIP as a whole.-->
<!--.................................................................................................-->
    
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
            <premis:objectIdentifierType><xsl:value-of select="$uri" />/<xsl:value-of select="$aip-id" /></premis:objectIdentifierType>
            <premis:objectIdentifierValue>1</premis:objectIdentifierValue>
        </premis:objectIdentifier>
    </xsl:template>
    
    
    <!--aip size: PREMIS 1.5.3 (optional): sum of every file size in bytes, formatted as a number.-->
    <xsl:template name="aip-size">
        <premis:size><xsl:value-of select="format-number(sum(//fileinfo/size),'#')" /></premis:size>
    </xsl:template>
    
    
    <!--aip format list: PREMIS 1.5.4 (required): gets a unique list of file formats in the aip.-->

    <!--Known issue: if different files are identified as the same format by different tools and not all the tools include a PUID, the format is in the list twice, once with the PUID and once without, to ensure complete information is captured-->

    <!--Known issue: if a format has multiple possible PUIDs because it has multiple possible versions, all PUIDs are in the same premis:formatRegistryKey element for each version since we do not know which one is associated with which version-->

    <xsl:template name="aip-unique-formats-list">

        <!--Uniqueness is determined by format name, version, and PUID.-->
        <xsl:for-each-group select="//identity" group-by="concat(@format,version,externalIdentifier[@type='puid'])">
            <xsl:sort select="current-grouping-key()" />

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

                <!--Complete list of tools that identified the format.-->
                <!--Uses absolute path (not current group) because different files of the same format may be identified by a different set of tools.-->
                <xsl:for-each select="//identity/tool">
                    <xsl:sort select="@toolname"/>

                    <!--Equivalent of the grouping key so can match tool to group.-->
                    <xsl:variable name="group" select="concat(../@format,following-sibling::version,following-sibling::externalIdentifier[@type='puid'])"/>

                    <!--Used to identify duplicate tools by combining the tool name with the group.-->
                    <xsl:variable name="dedup" select="concat(@toolname,$group)"/>

                    <!--Makes a format note for a tool if it matches this group and isn't a duplicate.-->
                    <!--Avoid duplicates by taking the last instance of a tool in the xml.-->  
                    <xsl:if test="$group=current-grouping-key() and not(following::tool[concat(@toolname,../@format,following-sibling::version,following-sibling::externalIdentifier[@type='puid'])=$dedup])">
                        <premis:formatNote>
                            <xsl:text>Format identified by </xsl:text>
                            <xsl:value-of select="@toolname" />
                            <xsl:text> version </xsl:text>
                            <xsl:value-of select="@toolversion" />
                        </premis:formatNote>
                    </xsl:if>
                </xsl:for-each>

                <!--Makes an invalid element to catch missing required information during validation.-->
                <xsl:if test="not(tool)"><premis:formatNote /></xsl:if>

            </premis:format>
        </xsl:for-each-group>
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
    
    
    <!--aip creating application list: PREMIS 1.5.5 (optional): gets a unique list of applications.-->
    <xsl:template name="aip-unique-creating-application-list">

        <!--Uniqueness is determed by application name and version.-->
        <xsl:for-each-group select="//fileinfo/creatingApplication" group-by="concat(creatingApplicationName,creatingApplicationVersion)">
            <xsl:sort select="current-grouping-key()" />

            <!--Application name, and also version if it has one.-->
            <!--Does not include version if there is no name. Will include in the filelist section.-->
            <!--Created date is only included in the filelist section.-->
            <xsl:if test="creatingApplicationName">
                <premis:creatingApplication>
                    <premis:creatingApplicationName>
                        <xsl:value-of select="creatingApplicationName" />
                    </premis:creatingApplicationName>
                    <xsl:if test="creatingApplicationVersion">
                        <premis:creatingApplicationVersion>
                            <xsl:value-of select="creatingApplicationVersion" />
                        </premis:creatingApplicationVersion>
                     </xsl:if>
                </premis:creatingApplication>
            </xsl:if>

        </xsl:for-each-group>
    </xsl:template>
    
    
    <!--aip inhibitors list: PREMIS 1.5.6 (required if applicable): gets a unique list of inhibitors.-->
    <xsl:template name="aip-unique-inhibitors-list">

        <!--Uniqueness is determined by inhibitor type and target.-->
        <xsl:for-each-group select="//fileinfo/inhibitor" group-by="concat(inhibitorType,inhibitorTarget)">
            <xsl:sort select="current-grouping-key()" />

            <!--Inhibitor type, and also target if it has one.-->
            <!--Does not include target if there is not type because that is not valid PREMIS.-->
            <xsl:if test="inhibitorType">
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
            </xsl:if>

        </xsl:for-each-group>
    </xsl:template>
    
    
    <!--aip relationship to collection: PREMIS 1.13 (required if applicable).-->
    <!--TODO: work for a partner for when they want a relationship-->
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
<!--FILELIST SECTION TEMPLATES -->

<!--Detailed information about each file in the aip. When tools generate conflicting information (i.e. 
multiple possible formats or multiple possible created dates) all possible information is kept. -->    <!--..................................................................................................-->

    <!--Creates the strcture for the premis:object for each file in the aip.-->
    <xsl:template match="fits">
        <premis:object>
            <xsl:call-template name="file-id" />
            <premis:objectCategory>file</premis:objectCategory>
            <premis:objectCharacteristics>
                <xsl:apply-templates select="fileinfo/md5checksum" />
                <xsl:apply-templates select="fileinfo/size" />
                <xsl:apply-templates select="identification/identity" />
                <xsl:if test="$workflow='website'">
                    <xsl:call-template name="warc" />
                </xsl:if>
                <xsl:apply-templates select="fileinfo/creatingApplication[string()]" />
                <xsl:apply-templates select="fileinfo/inhibitor[inhibitorType]" />
            </premis:objectCharacteristics>
            <xsl:call-template name="relationship-aip" />
        </premis:object>
    </xsl:template>
    
    
    <!--file id: PREMIS 1.1 (required): type is aip uri and value is file identifier from template.-->
    <xsl:template name="file-id">
        <premis:objectIdentifier>
            <premis:objectIdentifierType>
                <xsl:value-of select="$uri" />/<xsl:value-of select="$aip-id" />
            </premis:objectIdentifierType>
            <premis:objectIdentifierValue>
                <xsl:call-template name="get-file-id" />
            </premis:objectIdentifierValue>
        </premis:objectIdentifier>
    </xsl:template>
    

    <!--file MD5: PREMIS 1.5.2 (optional in preservation.xml).-->
    <xsl:template match="md5checksum">
        <xsl:variable name="md5" select="." />
        <premis:fixity>
            <premis:messageDigestAlgorithm>MD5</premis:messageDigestAlgorithm>
            <premis:messageDigest><xsl:value-of select="$md5" /></premis:messageDigest>
            <premis:messageDigestOriginator>
                <xsl:value-of select="$md5/@toolname" />
                <xsl:text> version </xsl:text>
                <xsl:value-of select="$md5/@toolversion" />
            </premis:messageDigestOriginator>
        </premis:fixity>
    </xsl:template>
    
    
    <!--file size: PREMIS 1.5.3 (optional): gets file size in bytes.-->
    <xsl:template match="size">
        <premis:size><xsl:value-of select="." /></premis:size>
    </xsl:template>
    
    
    <!--file format list: PREMIS 1.5.4 (required)-->
    <!--If different tools get different results, makes an element for each name/version variation.-->
    <xsl:template match="identity">

        <premis:format>

            <!--Format name, and verison if it has one.-->
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
            <xsl:if test="externalIdentifier[not(@type='puid')]"><premis:formatRegistry/></xsl:if>

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
                </premis:creatingApplicationVersion></xsl:if>

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
    
    
    <!--file relationship to aip: PREMIS 1.13 (required if applicable).-->
    <!--Type is group uri and value is aip id from variables.-->
    <xsl:template name="relationship-aip">
        <premis:relationship>
            <premis:relationshipType>structural</premis:relationshipType>
            <premis:relationshipSubType>Is Member Of</premis:relationshipSubType>
            <premis:relatedObjectIdentifier>
                <premis:relatedObjectIdentifierType>
                    <xsl:value-of select="$uri" />
                </premis:relatedObjectIdentifierType>
                <premis:relatedObjectIdentifierValue>
                    <xsl:value-of select="$aip-id" />
                </premis:relatedObjectIdentifierValue>
            </premis:relatedObjectIdentifier>
        </premis:relationship>
    </xsl:template>
    
    
<!--..................................................................................................-->
<!--CREATED DATE REFORMATTING TEMPLATE-->

<!--This template tests for each known date format and reformats it to the required YYYY-MM-DD by using regular expressions to extract the day, month, and year information and then reconfiguring them to the correct order and number of digits.-->

<!--If a new date format is encountered, the "otherwise" option will create an invalid premis:dateCreatedByApplication element so that the preservation.xml causes a validation error so staff know to update this stylesheet.-->
<!--..................................................................................................-->

    <xsl:template match="created">
        <xsl:variable name="apdate" select="." />
        <xsl:choose>
        
            <!--Does not include a date element if value is 0. -->
            <xsl:when test="$apdate='0'" />
            <xsl:when test="$apdate='0000:00:00 00:00:00'" />
            <xsl:when test="matches($apdate, '0-00-00T')" />

            <!--Pattern: Year:Month:Day Time and Year-Month-Day Time-->
            <!--Examples: 2018:01:02 01:02:33; 2000-10-05 9:15 PM-->
            <xsl:when test="matches($apdate, '^\d{4}(:|-)\d{2}(:|-)\d{2} ')">
                <premis:dateCreatedByApplication>
                    <!--Gets content before the space (removes time portion). -->
                    <xsl:variable name="dateString">
                        <xsl:value-of select="substring-before($apdate,' ')" />
                    </xsl:variable>
                    <!--Replaces any colon with a dash. -->
                    <xsl:value-of select="replace($dateString, ':', '-')" />
                </premis:dateCreatedByApplication>
            </xsl:when>
            
            <!--Pattern: Day.Month.Year(,) Time with all numbers-->
            <!--Examples: 23.07.98, 2:28 AM; 18.9.98, 12:50 PM; 2.9.98 11:42 PM-->
            <xsl:when test="matches($apdate, '(\d{1,2})\.(\d{1,2})\.(\d{2}),? \d{1,2}:\d{1,2} (AM|PM)')">
                <premis:dateCreatedByApplication>
                    <!--Gets the day, month, and year as separate regex groups.-->
                    <xsl:analyze-string select="$apdate" regex="(\d{{1,2}})\.(\d{{1,2}})\.(\d{{2}}),? \d{{1,2}}:\d{{1,2}} (AM|PM)">
                    
                        <!--Reformats each date component and recombines to make YYYY-MM-DD format. -->
                        <xsl:matching-substring>

                            <!--Year: makes four digits by adding '19' or '20'. -->
                            <xsl:variable name="year">
                                <xsl:choose>
                                    <!--If less than 50, assumes 21st century. -->
                                    <xsl:when test="number(regex-group(3)) &lt; 50">
                                        <xsl:text>20</xsl:text><xsl:value-of select="regex-group(3)" />
                                    </xsl:when>
                                    <!--If 50 or more, assumes 20th century. -->
                                    <xsl:otherwise>
                                        <xsl:text>19</xsl:text><xsl:value-of select="regex-group(3)" />
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>

                            <!--Month: adds leading zero if not already a two-digit number. -->
                            <xsl:variable name="month">
                                <xsl:value-of select="format-number(number(regex-group(2)),'00')" />
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
            <!--Examples: 12/01/99 12:01 PM; 1/5/2011 1:11:55 --> 
            <xsl:when test="matches($apdate, '\d{1,2}/\d{1,2}/\d{2,4}')">
                <premis:dateCreatedByApplication>
                    <!--Gets the day, month, and year as separate regex groups. -->
                    <xsl:analyze-string select="$apdate" regex="(\d{{1,2}})/(\d{{1,2}})/(\d{{2,4}})">

                        <!--Reformats each date component and recombines to make YYYY-MM-DD format. -->
                        <xsl:matching-substring>

                            <!--Year: makes four digits by adding '19' or '20'. -->
                            <xsl:variable name="year">
                                <xsl:choose>
                                    <!--Already a four digit year. Leave as is. -->
                                    <xsl:when test="number(regex-group(3)) &gt; 999">
                                        <xsl:value-of select="regex-group(3)" />
                                    </xsl:when>
                                    <!--If less than 50, assumes 21st century. -->
                                    <xsl:when test="number(regex-group(3)) &lt; 50">
                                        <xsl:text>20</xsl:text><xsl:value-of select="regex-group(3)" />
                                    </xsl:when>
                                    <!--If 50 or more, assumes 20th century. -->
                                    <xsl:otherwise>
                                        <xsl:text>19</xsl:text><xsl:value-of select="regex-group(3)" />
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>

                            <!--Month: adds leading zero if not already a two-digit number. -->
                            <xsl:variable name="month">
                                <xsl:value-of select="format-number(number(regex-group(1)),'00')" />
                            </xsl:variable>

                            <!--Day: adds leading zero if not already a two-digit number. -->
                            <xsl:variable name="day">
                                <xsl:value-of select="format-number(number(regex-group(2)),'00')" />
                            </xsl:variable>

                            <!--Combines the date components in the correct order -->
                            <xsl:value-of select="$year, $month, $day" separator="-" />

                        </xsl:matching-substring>
                    </xsl:analyze-string>
                </premis:dateCreatedByApplication>
            </xsl:when>

            <!--Pattern: (Day of Week) Month ( )Day(,) (Time) Year with month spelled out-->
            <!--Content in the parenthesis may or may not be present. -->
            <!--Examples: May 5, 2004; Monday, January 7, 2001 11:22:33 PM; 
                          Wed Mar 01 11:22:33 EST 2003; Thu Apr  2 20:05:01 1998 -->
            <xsl:when test="matches($apdate, '[a-zA-Z]+  ?\d{1,2},? [0-9:A-Z ]*\d{4}')">
                <premis:dateCreatedByApplication>
                    <!--Gets the day, month, and year as separate regex groups. -->
                    <xsl:analyze-string select="$apdate" regex="([a-zA-Z]+)  ?(\d{{1,2}}),? [0-9:A-Z ]*(\d{{4}})">
                        <!--Reformats each date component and recombines to make YYYY-MM-DD format. -->
                        <xsl:matching-substring>

                            <!--Year: already formatted correctly. -->
                            <xsl:variable name="year">
                                <xsl:value-of select="regex-group(3)" />
                            </xsl:variable>

                            <!--Month: converts from word or abbreviation to two-digit number. -->
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

                            <!--Day: adds leading zero if not already a two-digit number. -->
                            <xsl:variable name="day">
                                <xsl:value-of select="format-number(number(regex-group(2)),'00')" />
                            </xsl:variable>

                            <!--Combines the date components in the correct order -->
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
