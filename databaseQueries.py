from gql import gql

findFabric = gql(
  """
  query ListWebFabricItems($filter: ModelWebFabricItemsFilterInput!) {
    listWebFabricItems(filter: $filter ){
      items {
        id
        name
      }
    }
  }
  """
)

patternQuery = gql(
  """
  mutation($input: CreateWebPatternItemsInput!) {
    createWebPatternItems(input:$input) {
      id
      name
    }
  
  }
  """
)

fabricQuery = gql(
"""
  mutation($input: CreateWebFabricItemsInput!) {    
    createWebFabricItems(input:$input) {
        id
        name
    }
  }
"""
)

joinQuery = gql(
"""
    mutation CreateFabricToPatterns($input: CreateFabricToPatternsInput!) {
        createFabricToPatterns(input:$input) {
            id
            webPatternItemsId
            webFabricItemsId
        }
    }
"""
)

def createMutationInput(name):
  variables = {"input": {
      "name": name,
  }}
  return variables

def createFilterInput(name):
  variables = {"filter": 
    {
      "name": 
        {
        "contains": name
        }
    }
  }
  return variables

def createJoinInput(fabricId,patternId):
  input = {
      "input": {
          "webPatternItemsId": patternId,
          "webFabricItemsId":  fabricId
      }
  }
  return input

