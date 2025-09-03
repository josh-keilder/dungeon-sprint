from settings import *

atlas_texture_data = {
    0:{'name':'dungeon_left_wall_1','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(0,0)},
    1:{'name':'dungeon_top_wall_1','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(1,0)},
    2:{'name':'dungeon_top_wall_2','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(2,0)},
    3:{'name':'dungeon_top_wall_3','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(3,0)},
    4:{'name':'dungeon_top_wall_4','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(4,0)},
    5:{'name':'dungeon_right_wall_1','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(5,0)},
    6:{'name':'dungeon_floor_1','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(6,0)},
    7:{'name':'dungeon_floor_2','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(7,0)},
    8:{'name':'dungeon_floor_3','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(8,0)},
    9:{'name':'dungeon_floor_4','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(9,0)},
    
    10:{'name':'dungeon_left_wall_2','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(0,1)},
    11:{'name':'dungeon_floor_1','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(1,1)},
    12:{'name':'dungeon_floor_2','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(2,1)},
    13:{'name':'dungeon_floor_3','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(3,1)},
    14:{'name':'dungeon_floor_4','type':'floor', 'size':(TILESIZE,TILESIZE),'position':(4,1)},
    15:{'name':'dungeon_right_wall_2','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(5,1)},
    16:{'name':'dungeon_floor_5','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(6,1)},
    17:{'name':'dungeon_floor_6','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(7,1)},
    18:{'name':'dungeon_floor_7','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(8,1)},
    19:{'name':'dungeon_floor_8','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(9,1)},

    20:{'name':'dungeon_left_wall_3','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(0,2)},
    21:{'name':'dungeon_floor_5','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(1,2)},
    22:{'name':'dungeon_floor_6','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(2,2)},
    23:{'name':'dungeon_floor_7','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(3,2)},
    24:{'name':'dungeon_floor_8','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(4,2)},
    25:{'name':'dungeon_right_wall_3','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(5,2)},
    26:{'name':'dungeon_floor_9','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(6,2)},
    27:{'name':'dungeon_floor_10','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(7,2)},
    28:{'name':'dungeon_floor_11','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(8,2)},
    29:{'name':'dungeon_floor_12','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(9,2)},

    30:{'name':'dungeon_left_wall_4','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(0,3)},
    31:{'name':'dungeon_floor_9','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(1,3)},
    32:{'name':'dungeon_floor_10','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(2,3)},
    33:{'name':'dungeon_floor_11','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(3,3)},
    34:{'name':'dungeon_floor_12','type':'floor', 'size':(TILESIZE,TILESIZE), 'position':(4,3)},
    35:{'name':'dungeon_right_wall_4','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(5,3)},
    36:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(6,3)},
    37:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(7,3)},
    38:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(8,3)},
    39:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(9,3)},

    40:{'name':'dungeon_bottom_left_corner_wall','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(0,4)},
    41:{'name':'bottom_wall_1','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(1,4)},
    42:{'name':'bottom_wall_2','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(2,4)},
    43:{'name':'bottom_wall_3','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(3,4)},
    44:{'name':'bottom_wall_4','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(4,4)},
    45:{'name':'dungeon_bottom_right_corner_wall','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(5,4)},
    46:{'name':'center_breakable_door_top','type':'breakable_door', 'size':(TILESIZE,TILESIZE), 'position':(6,4)},
    47:{'name':'left_breakable_door_top','type':'breakable_door', 'size':(TILESIZE,TILESIZE), 'position':(7,4)},
    48:{'name':'right_breakable_door_top','type':'breakable_door', 'size':(TILESIZE,TILESIZE), 'position':(8,4)},
    49:{'name':'large_pots','type':'breakable_pots', 'size':(TILESIZE,TILESIZE), 'position':(9,4)},

    50:{'name':'dungeon_top_left_corner_wall_1','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(0,5)},
    51:{'name':'top_wall_1','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(1,5)},
    52:{'name':'top_wall_2','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(2,5)},
    53:{'name':'dungeon_top_right_corner_wall_1','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(3,5)},
    54:{'name':'dungeon_top_left_corner_wall_2','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(4,5)},
    55:{'name':'dungeon_top_right_corner_wall_2','type':'wall', 'size':(TILESIZE,TILESIZE), 'position':(5,5)},
    56:{'name':'center_breakable_door_bottom','type':'breakable_door', 'size':(TILESIZE,TILESIZE), 'position':(6,5)},
    57:{'name':'left_breakable_door_bottom','type':'breakable_door', 'size':(TILESIZE,TILESIZE), 'position':(7,5)},
    58:{'name':'right_breakable_door_bottom','type':'breakable_door', 'size':(TILESIZE,TILESIZE), 'position':(8,5)},
    59:{'name':'small_pots','type':'breakable_pots', 'size':(TILESIZE,TILESIZE), 'position':(9,5)},

    60:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(0,6)},
    61:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(1,6)},
    62:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(2,6)},
    63:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(3,6)},
    64:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(4,6)},
    65:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(5,6)},
    66:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(6,6)},
    67:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(7,6)},
    68:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(8,6)},
    69:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(9,6)},

    70:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(0,7)},
    71:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(1,7)},
    72:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(2,7)},
    73:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(3,7)},
    74:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(4,7)},
    75:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(5,7)},
    76:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(6,7)},
    77:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(7,7)},
    78:{'name':'void','type':'void', 'size':(TILESIZE,TILESIZE), 'position':(8,7)},
    79:{'name':' ','type':'unused', 'size':(TILESIZE,TILESIZE), 'position':(9,7)},

    # 'player':{'type':'player', 'file_path':'Assets/Proto_Idle_Down.png', 'size':(PLAYER_SPRITESIZE,PLAYER_SPRITESIZE), 'position':(0,0)}
}

solo_texture_data = {
   'player':{'type':'player', 'file_path':'Assets/Proto_Idle_Down.png', 'size':(PLAYER_SPRITESIZE,PLAYER_SPRITESIZE), 'position':(0,0)}
}


player_texture_data = {
    'player':{'type':'player', 'size':(PLAYER_SPRITESIZE,PLAYER_SPRITESIZE), 'position':(0,0)}
}
