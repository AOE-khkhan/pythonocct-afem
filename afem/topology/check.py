#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 Laughlin Research, L.L.C.
#
# This file is subject to the license agreement that was delivered
# with this source code.
#
# THE SOFTWARE AND INFORMATION ARE PROVIDED ON AN AS "AS IS" BASIS,
# WITHOUT ANY WARRANTIES OR REPRESENTATIONS EXPRESS, IMPLIED OR
# STATUTORY; INCLUDING, WITHOUT LIMITATION, WARRANTIES OF QUALITY,
# PERFORMANCE, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.

from OCCT.BRep import BRep_Builder, BRep_Tool
from OCCT.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge,
                                 BRepBuilderAPI_MakeFace,
                                 BRepBuilderAPI_MakeVertex,
                                 BRepBuilderAPI_MakeWire)
from OCCT.BRepCheck import BRepCheck_Analyzer
from OCCT.BRepClass3d import BRepClass3d_SolidClassifier
from OCCT.ShapeAnalysis import ShapeAnalysis_Edge
from OCCT.TopAbs import (TopAbs_COMPOUND, TopAbs_COMPSOLID, TopAbs_EDGE,
                         TopAbs_FACE, TopAbs_IN, TopAbs_ON, TopAbs_OUT,
                         TopAbs_SHELL,
                         TopAbs_SOLID, TopAbs_UNKNOWN, TopAbs_VERTEX,
                         TopAbs_WIRE)
from OCCT.TopoDS import (TopoDS_CompSolid, TopoDS_Compound, TopoDS_Edge,
                         TopoDS_Face, TopoDS_Shape, TopoDS_Shell, TopoDS_Solid,
                         TopoDS_Vertex, TopoDS_Wire, TopoDS)
from OCCT.gp import gp_Pnt

from afem.geometry.check import CheckGeom

__all__ = ["CheckShape", "ClassifyPointInSolid"]


class CheckShape(object):
    """
    Check shape.
    """

    @staticmethod
    def is_shape(shape):
        """
        Check if entity is a shape.

        :param shape: The shape.

        :return: *True* if a shape, *False* if not.
        :rtype: bool
        """
        return isinstance(shape, TopoDS_Shape)

    @staticmethod
    def is_shell(shape):
        """
        Check if the shape is a shell.

        :param OCCT.TopoDS.TopoDS_Shape shape: The shape.

        :return: *True* if a shell, *False* if not.
        :rtype: bool
        """
        try:
            return shape.ShapeType() == TopAbs_SHELL
        except AttributeError:
            return False

    @staticmethod
    def is_solid(shape):
        """
        Check if the shape is a solid.

        :param OCCT.TopoDS.TopoDS_Shape shape: The shape.

        :return: *True* if a solid, *False* if not.
        :rtype: bool
        """
        try:
            return shape.ShapeType() == TopAbs_SOLID
        except AttributeError:
            return False

    @classmethod
    def is_valid(cls, shape):
        """
        Check the shape for errors.

        :param OCCT.TopoDS.TopoDS_Shape shape: The shape.

        :return: *True* if valid, *False* if not.
        :rtype: bool
        """
        return BRepCheck_Analyzer(shape, True).IsValid()

    @staticmethod
    def is_seam(edge, face):
        """
        Check to see if the edge is a seam edge on the face.

        :param OCCT.TopoDS.TopoDS_Edge edge: The edge.
        :param OCCT.TopoDS.TopoDS_Face face: The face.

        :return: *True* if a seam, *False* if not.
        :rtype: bool
        """
        return ShapeAnalysis_Edge().IsSeam(edge, face)

    @classmethod
    def to_vertex(cls, entity):
        """
        Convert an entity to a vertex.

        :param entity: The entity.

        :return: A vertex.
        :rtype: OCCT.TopoDS.TopoDS_Vertex

        :raise TypeError: If entity cannot be converted to a vertex.
        """
        if isinstance(entity, TopoDS_Vertex):
            return entity

        if isinstance(entity, gp_Pnt):
            return BRepBuilderAPI_MakeVertex(entity).Vertex()

        if CheckGeom.is_point_like(entity):
            p = gp_Pnt(entity[0], entity[1], entity[2])
            return BRepBuilderAPI_MakeVertex(p).Vertex()

        if cls.is_shape(entity) and entity.ShapeType() == TopAbs_VERTEX:
            return TopoDS.Vertex_(entity)

        raise TypeError('Failed to convert entity to a vertex.')

    @classmethod
    def to_edge(cls, entity):
        """
        Convert an entity to an edge.

        :param entity: The entity.

        :return: An edge.
        :rtype: OCCT.TopoDS.TopoDS_Edge

        :raise TypeError: If entity cannot be converted to an edge.
        """
        if isinstance(entity, TopoDS_Edge):
            return entity

        if CheckGeom.is_curve(entity):
            return BRepBuilderAPI_MakeEdge(entity.handle).Edge()

        if cls.is_shape(entity) and entity.ShapeType() == TopAbs_EDGE:
            return TopoDS.Edge_(entity)

        raise TypeError('Failed to convert entity to an edge.')

    @classmethod
    def to_wire(cls, entity):
        """
        Convert an entity to a wire.

        :param entity: The entity.

        :return: A wire.
        :rtype: OCCT.TopoDS.TopoDS_Wire

        :raise TypeError: If entity cannot be converted to a wire.
        """
        if isinstance(entity, TopoDS_Wire):
            return entity

        if CheckGeom.is_curve(entity):
            e = BRepBuilderAPI_MakeEdge(entity.handle).Edge()
            return BRepBuilderAPI_MakeWire(e).Wire()

        if cls.is_shape(entity) and entity.ShapeType() == TopAbs_EDGE:
            return BRepBuilderAPI_MakeWire(entity).Wire()

        if cls.is_shape(entity) and entity.ShapeType() == TopAbs_WIRE:
            return TopoDS.Wire_(entity)

        raise TypeError('Failed to convert entity to a wire.')

    @classmethod
    def to_face(cls, entity):
        """
        Convert an entity to a face.

        :param entity: The entity.

        :return: A face.
        :rtype: OCCT.TopoDS.TopoDS_Face

        :raise TypeError: If entity cannot be converted to a face.
        """
        if isinstance(entity, TopoDS_Face):
            return entity

        if CheckGeom.is_surface(entity):
            return BRepBuilderAPI_MakeFace(entity.handle, 0.).Face()

        if cls.is_shape(entity) and entity.ShapeType() == TopAbs_FACE:
            return TopoDS.Face_(entity)

        raise TypeError('Failed to convert entity to a face.')

    @classmethod
    def to_shell(cls, entity):
        """
        Convert an entity to a shell.

        :param entity: The entity.

        :return: A shell.
        :rtype: OCCT.TopoDS.TopoDS_Shell

        :raise TypeError: If entity cannot be converted to a shell.
        """
        if isinstance(entity, TopoDS_Shell):
            return entity

        if cls.is_shape(entity) and entity.ShapeType() == TopAbs_SHELL:
            return TopoDS.Shell_(entity)

        if cls.is_shape(entity) and entity.ShapeType() == TopAbs_FACE:
            shell = TopoDS_Shell()
            builder = BRep_Builder()
            builder.MakeShell(shell)
            builder.Add(shell, entity)
            return shell

        if CheckGeom.is_surface(entity):
            f = BRepBuilderAPI_MakeFace(entity.handle, 0.).Face()
            shell = TopoDS_Shell()
            builder = BRep_Builder()
            builder.MakeShell(shell)
            builder.Add(shell, f)
            return shell

        raise TypeError('Failed to convert entity to a shell.')

    @classmethod
    def to_solid(cls, entity):
        """
        Convert an entity to a solid.

        :param entity: The entity.

        :return: A solid.
        :rtype: OCCT.TopoDS.TopoDS_Solid

        :raise TypeError: If entity cannot be converted to a solid.
        """
        if isinstance(entity, TopoDS_Solid):
            return entity

        if cls.is_shape(entity) and entity.ShapeType() == TopAbs_SOLID:
            return TopoDS.Solid_(entity)

        raise TypeError('Failed to convert entity to a solid.')

    @classmethod
    def to_compsolid(cls, entity):
        """
        Convert an entity to a compsolid.

        :param entity: The entity.

        :return: A compsolid.
        :rtype: OCCT.TopoDS.TopoDS_CompSolid

        :raise TypeError: If entity cannot be converted to a compsolid.
        """
        if isinstance(entity, TopoDS_CompSolid):
            return entity

        if cls.is_shape(entity) and entity.ShapeType() == TopAbs_COMPSOLID:
            return TopoDS.CompSolid_(entity)

        raise TypeError('Failed to convert entity to a compsolid.')

    @classmethod
    def to_compound(cls, entity):
        """
        Convert an entity to a compound.

        :param entity: The entity.

        :return: A compound
        :rtype: OCCT.TopoDS.TopoDS_Compound

        :raise TypeError: If entity cannot be converted to a compound.
        """
        if isinstance(entity, TopoDS_Compound):
            return entity

        if cls.is_shape(entity) and entity.ShapeType() == TopAbs_COMPOUND:
            return TopoDS.Compound_(entity)

        if cls.is_shape(entity):
            cp = TopoDS_Compound
            builder = BRep_Builder()
            builder.MakeCompound(cp)
            builder.Add(cp, entity)
            return cp

        raise TypeError('Failed to convert entity to a compound.')

    @classmethod
    def to_shape(cls, entity):
        """
        Convert the entity to a shape. This method tries to convert the
        entity to its most specific shape type.

        :param entity: The entity.

        :return: A shape.
        :rtype: OCCT.TopoDS.TopoDS_Shape

        :raise TypeError: If entity cannot be converted to a shape.
        """
        if entity is None:
            return None

        # Shapes
        if isinstance(entity, TopoDS_Shape):
            if entity.ShapeType() == TopAbs_VERTEX:
                return TopoDS.Vertex_(entity)
            elif entity.ShapeType() == TopAbs_EDGE:
                return TopoDS.Edge_(entity)
            elif entity.ShapeType() == TopAbs_WIRE:
                return TopoDS.Wire_(entity)
            elif entity.ShapeType() == TopAbs_FACE:
                return TopoDS.Face_(entity)
            elif entity.ShapeType() == TopAbs_SHELL:
                return TopoDS.Shell_(entity)
            elif entity.ShapeType() == TopAbs_SOLID:
                return TopoDS.Solid_(entity)
            elif entity.ShapeType() == TopAbs_COMPSOLID:
                return TopoDS.CompSolid_(entity)
            elif entity.ShapeType() == TopAbs_COMPOUND:
                return TopoDS.Compound_(entity)
            else:
                raise TypeError('Failed to convert entity to a shape.')

        # Geometry
        if CheckGeom.is_point_like(entity):
            return cls.to_vertex(entity)
        if CheckGeom.is_curve(entity):
            return cls.to_edge(entity)
        if CheckGeom.is_surface(entity):
            return cls.to_face(entity)

        raise TypeError('Failed to convert entity to a shape.')

    @staticmethod
    def same_parameter(edge):
        """
        Returns the SameParameter flag for the edge.

        :param OCCT.TopoDS.TopoDS_Edge edge: The edge.

        :return: The same parameter flag.
        :rtype: bool
        """
        return BRep_Tool.SameParameter_(edge)

    @staticmethod
    def same_range(edge):
        """
        Returns the SameRange flag for the edge.

        :param OCCT.TopoDS.TopoDS_Edge edge: The edge.

        :return: The same range flag.
        :rtype: bool
        """
        return BRep_Tool.SameRange_(edge)


class ClassifyPointInSolid(object):
    """
    Classify a point in a solid.

    :param OCCT.TopoDS.TopoDS_Solid solid: The solid.
    :param point_like pnt: The point. If not provided the *perform()* method
        will need to be used.
    :param float tol: The tolerance.
    """

    def __init__(self, solid, pnt=None, tol=1.0e-7):
        pnt = CheckGeom.to_point(pnt)

        if not CheckGeom.is_point(pnt):
            self._tool = BRepClass3d_SolidClassifier(solid)
        else:
            self._tool = BRepClass3d_SolidClassifier(solid, pnt, tol)

    def perform(self, pnt, tol=1.0e-7):
        """
        Perform the classification with the point and tolerance.

        :param point_like pnt: The point.
        :param float tol: The tolerance.

        :return: None.
        """
        pnt = CheckGeom.to_point(pnt)
        self._tool.Perform(pnt, tol)

    @property
    def is_in(self):
        """
        :return: *True* if point is in solid, *False* if not.
        :rtype: bool
        """
        return self._tool.State() == TopAbs_IN

    @property
    def is_out(self):
        """
        :return: *True* if point is outside the solid, *False* if not.
        :rtype: bool
        """
        return self._tool.State() == TopAbs_OUT

    @property
    def is_on(self):
        """
        :return: *True* if point is on the solid, *False* if not.
        :rtype: bool
        """
        return self._tool.State() == TopAbs_ON

    @property
    def is_unknown(self):
        """
        :return: *True* if classification is unknown, *False* if not.
        :rtype: bool
        """
        return self._tool.State() == TopAbs_UNKNOWN

    @property
    def is_on_face(self):
        """
        :return: *True* if point is on a face, *False* if not.
        :rtype: bool
        """
        return self._tool.IsOnAFace()

    def face(self):
        """
        Get the face the point is on.

        :return: The face.
        :rtype: OCCT.TopoDS.TopoDS_Face
        """
        return self._tool.Face()
