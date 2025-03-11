<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output method="xml" encoding="UTF-8" indent="yes"/>
	<xsl:decimal-format name="dformat" decimal-separator="." grouping-separator=","/>

  <!--Include templates/rules for: styles-->
  <xsl:include href="simpleLineStyle.xsl"/>
  <xsl:include href="textStyle.xsl"/>
  
  <!--Include templates/rules for: GeoFeature-->
  <xsl:include href="SeaIce.xsl"/>
  <xsl:include href="LakeIce.xsl"/>
  <xsl:include href="Iceberg.xsl"/>
  <xsl:include href="IceLead.xsl"/>
  <xsl:include href="IceThickness.xsl"/>
  <xsl:include href="IceEdge.xsl"/>
  <xsl:include href="IcebergLimit.xsl"/>
  <xsl:include href="SnowCover.xsl"/>
  <xsl:include href="StageOfMelt.xsl"/>
  <xsl:include href="IceKeelBummock.xsl"/>

  
  <!--Include templates/rules for: MetaFeature-->
  <xsl:include href="DataCoverage.xsl"/>

  
  <!--Include templates/rules for: Default-->
  <xsl:include href="Default.xsl"/>

	<xsl:template match="/">
		<displayList>
			<xsl:apply-templates select="Dataset/Features/*"/>
		</displayList>
	</xsl:template>
</xsl:transform>
